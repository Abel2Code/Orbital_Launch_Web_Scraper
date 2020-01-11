from collections import Counter
import csv
import bs4
import itertools
import csv
import requests
import sys

URL = 'https://en.wikipedia.org/wiki/2019_in_spaceflight'
YEAR = 2019

MONTH_MAP = {
	'January'   : 1,
	'February'  : 2,
	'March'     : 3,
	'April'     : 4,
	'May'       : 5,
	'June'      : 6,
	'July'      : 7,
	'August'    : 8,
	'September' : 9,
	'October'   : 10,
	'November'  : 11,
	'December'  : 12,
}

MONTH_LENGTHS_2019 = {
	'January'   : 31,
	'February'  : 28,
	'March'     : 31,
	'April'     : 30,
	'May'       : 31,
	'June'      : 30,
	'July'      : 31,
	'August'    : 31,
	'September' : 30,
	'October'   : 31,
	'November'  : 30,
	'December'  : 31,
}

def main():
	try:
		r = requests.get(URL)
	except requests.exceptions.RequestException as exception:
		print(exception)
		sys.exit(1)

	if(not r.ok):
		raise Error(f"Could not reach {URL}")

	html_obj = bs4.BeautifulSoup(r.text, "html.parser")


	ol_header = html_obj.find(id='Orbital_launches')

	# Find Orbital Launch Table
	wikitable = ol_header.find_next('table', {"class":"wikitable"})

	table_rows = wikitable.find_all('tr')


	current_date = None
	successful_launches = Counter()
	for tr in table_rows:
		td = tr.find_all('td')
		td_len = len(td)

		# If table length is not of length 5 or 6, reset current date and continue
		if td_len not in [5,6]:
			current_date = None
			continue

		# If table length is 5, check that it has a date. If so, set current date.
		if td_len == 5:
			current_date = format_date(td[0])
			continue

		# If current_date is set and a spacecraft is found, update dictionary for that date
		# NOTE: If date is NONE, a successful launch has already been found for that launch\
		if current_date and td_len == 6:
			outcome = td[5].get_text().rstrip()

			# NOTE: There may be situations where status ends in [NUM]. This gets only the status
			outcome = ''.join(itertools.takewhile(lambda x: x.isalpha(), outcome))

			if outcome in  outcome in ["Operational", "Successful", "En Route"]:
				successful_launches[current_date] += 1
				current_date = None

	write_launches_to_file(successful_launches)


def write_launches_to_file(successful_launches):
	FILE_NAME = 'output.csv'
	with open(FILE_NAME, mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)

		writer.writerow(['date',' value'])

		for month_i, month in enumerate(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']):
			for day_i in range(MONTH_LENGTHS_2019[month]):
				month_num, day_num = month_i+1, day_i+1
				date = date_generator(day_num, month_num, YEAR)
				writer.writerow([f'{date}T00:00:00+00:00', f' {successful_launches[date]}'])


# HELPER FUNCTIONS

# Returns formatted date or NONE if invalid str
def format_date(s: str):
	s = s.get_text().rstrip()

	s_split = s.split(' ')

	if len(s_split) != 2:
		return None

	day_num, month = s_split

	if not day_num.isdigit():
		return None

	day_num = int(day_num)
	month = ''.join(itertools.takewhile(lambda x: x.isalpha(), month))

	month_num = MONTH_MAP.get(month, -1)
	if month_num > 0:
		date = date_generator(day_num, month_num, YEAR)
		return date

	return None

def date_generator(day_num: int, month_num: int, year: int):
	return f'{YEAR}-{month_num:0>2d}-{day_num:0>2d}'


if __name__ == '__main__':
	main()
