import pandas as pd


def load_cleaned(path: str = 'data/cleaned.csv'):
	df = pd.read_csv(path)
	return df


def filter_data(df, type_value=None, decades=None, genres=None):
	data = df.copy()

	if type_value:
		data = data[data['type'].str.upper() == type_value.upper()]

	if decades and len(decades) == 2:
		# decades are strings like "1970s" -> take first 4 chars
		def decade_to_int(x):
			try:
				return int(str(x)[:4])
			except Exception:
				return None
		start_dec = decade_to_int(decades[0])
		end_dec = decade_to_int(decades[1])
		if start_dec is not None and end_dec is not None and 'decade' in data.columns:
			d_int = data['decade'].astype(str).str[:4].astype('int', errors='ignore')
			data = data[(d_int >= start_dec) & (d_int <= end_dec)]

	if genres and len(genres) > 0 and 'genres' in data.columns:
		# genres stored as strings like "['drama','crime']"; ensure list
		def has_any(lst):
			if not isinstance(lst, list):
				return False
			return any(g in lst for g in genres)
		# try to eval strings to list
		parsed = []
		for v in data['genres']:
			if isinstance(v, list):
				parsed.append(v)
			else:
				try:
					parsed.append(eval(v))
				except Exception:
					parsed.append([])
		data = data.copy()
		data['__genres_list'] = parsed
		data = data[data['__genres_list'].apply(has_any)]
		data = data.drop(columns=['__genres_list'])

	return data


def titles_per_decade(df):
	if 'decade' not in df.columns:
		return pd.DataFrame({'decade': [], 'count': []})
	out = df.groupby('decade').size().reset_index(name='count').sort_values('decade')
	return out


def top_genres(df, n=10):
	if 'genres' not in df.columns:
		return pd.DataFrame({'genre': [], 'count': []})
	# ensure list
	rows = []
	for v in df['genres']:
		if isinstance(v, list):
			rows.extend(v)
		else:
			try:
				rows.extend(eval(v))
			except Exception:
				pass
	s = pd.Series(rows)
	counts = s.value_counts().head(n)
	return counts.reset_index().rename(columns={'index': 'genre', 0: 'count'})


def score_distribution(df, score_col='imdb_score'):
	if score_col not in df.columns:
		return df[[score_col]].dropna()  # will error; simple return
	return df[[score_col]].dropna()


def best_imdb_each_year(df):
	if 'imdb_score' not in df.columns or 'release_year' not in df.columns:
		return pd.DataFrame({'release_year': [], 'title': [], 'imdb_score': []})
	# keep rows with year
	temp = df.dropna(subset=['release_year', 'imdb_score'])
	temp['release_year'] = temp['release_year'].astype(int, errors='ignore')
	# idxmax per year
	idx = temp.groupby('release_year')['imdb_score'].idxmax()
	out = temp.loc[idx, ['release_year', 'title', 'imdb_score']].sort_values('release_year')
	return out


def country_counts(df):
	if 'production_countries' not in df.columns:
		return pd.DataFrame({'country': [], 'count': []})
	rows = []
	for v in df['production_countries']:
		if isinstance(v, list):
			rows.extend(v)
		else:
			try:
				rows.extend(eval(v))
			except Exception:
				pass
	s = pd.Series(rows)
	counts = s.value_counts()
	return counts.reset_index().rename(columns={'index': 'country', 0: 'count'})


def top_popular(df, n=20):
	if 'tmdb_popularity' not in df.columns:
		return pd.DataFrame({'title': [], 'tmdb_popularity': []})
	temp = df.dropna(subset=['tmdb_popularity'])
	out = temp.sort_values('tmdb_popularity', ascending=False).head(n)
	return out[['title', 'tmdb_popularity', 'release_year']]


def imdb_vs_tmdb(df):
	# return rows with both scores present for comparison
	cols = ['imdb_score', 'tmdb_score']
	keep = [c for c in cols if c in df.columns]
	if len(keep) < 2:
		return pd.DataFrame(columns=['imdb_score', 'tmdb_score'])
	x = df.dropna(subset=keep)
	return x

