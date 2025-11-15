import ast #tool for parsing Python code
import pandas as pd

def parseList(value): # convert a value like "['drama', 'crime']" (a string) into a Python list
    #---> input values: could be NaN, a string, a list, or other types
    
    #If value is missing or NaN returns None
	if pd.isna(value):
		return None

	#If value is already a list returns it unchanged
	if isinstance(value, list):
		return value

	#If it’s a string 
	if isinstance(value, str):
		#Strips whitespace 
		text = value.strip()
		#if empty returns None
		if not text:
			return None
		try:
			#Tries ast.literal_eval(text) to safely evaluate Lists
			parsed = ast.literal_eval(text)
			if isinstance(parsed, list):
				#If parsed is a list then normalize all items to strings and return
				return [str(x) for x in parsed]
			#If parsed is a single value then return that value as a one-item list
			return [str(parsed)] if parsed is not None else None
		#If literal_eval fails, it falls back to splitting on commas
		except Exception:
			# fallback: split by comma
			return [t.strip().strip("'\"") for t in text.split(',') if t.strip()]
	#For any other type returns [str(value)]
	return [str(value)]

def clean_data(): #Loads the CSV and performs the full cleaning pipeline on data/data.csv.
    #---> uses the fixed CSV path: data/data.csv
    
	df = pd.read_csv('data/data.csv')
 
	# 1) Basic string cleanup
	
	# convert the column "title" to pandas “string” dtype and strip spaces
	if 'title' in df.columns:
		df['title'] = df['title'].astype('string').str.strip()
  	#strip in the column "type" spaces and convert to UPPERCASE (e.g., MOVIE or SHOW)
	if 'type' in df.columns:
		df['type'] = df['type'].astype('string').str.strip().str.upper()

	# 2) Parse List columns
	for col in ['genres', 'production_countries']:
		if col in df.columns:
			df[col] = df[col].apply(parseList)

	# 3) Parse Number columns
	for col in ['release_year', 'runtime', 'seasons', 'imdb_votes']:
		if col in df.columns:
			df[col] = pd.to_numeric(df[col], errors='coerce')
	for col in ['imdb_score', 'tmdb_popularity', 'tmdb_score']:
		if col in df.columns:
			df[col] = pd.to_numeric(df[col], errors='coerce')

	# 4) Helpful derived columns (simplified)
	if 'genres' in df.columns:
		df['primary_genre'] = df['genres'].apply(lambda x: x[0] if isinstance(x, list) and x else None)
	if 'release_year' in df.columns:
		def to_decade(y):
			if pd.isna(y):
				return None
			return f"{int(y)//10*10}s"
		df['decade'] = df['release_year'].apply(to_decade)

	# 5) Drop duplicate ids if present (if they exist)
	if 'id' in df.columns:
		df = df.drop_duplicates(subset=['id'], keep='first').reset_index(drop=True)
	return df

def save_cleaned_data(df, output_path): #Save a cleaned DataFrame to a CSV file.
    
	# Convert lists back to strings so CSV can store them
	for col in ['genres', 'production_countries']:
		if col in df.columns:
			df[col] = df[col].apply(lambda x: str(x) if isinstance(x, list) else x)
	df.to_csv(output_path, index=False)
