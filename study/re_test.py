import re
pattern  = r'[\s\,]+'
str = 'www.gogodj.com,7719643,a,b, c d,';
print(re.split(pattern ,str))

pattern = r'www\.(\w+)\.(\w+)'
match = re.match(pattern ,str)
print(match)
if match:
     matched_url = match.groups()
     print(matched_url)

 

