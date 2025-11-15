import streamlit as st
import pandas as pd
import os, sys
import pycountry
import plotly.io as pio
import csv


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
	sys.path.insert(0, ROOT)

from source import analysis as an
from source import visuals as vz


st.set_page_config(page_title='MovieMind', layout='wide')

# Global Plotly style closer to a modern, minimal feel
pio.templates.default = 'plotly_dark'


def load_data():
	df = an.load_cleaned('data/cleaned.csv')
	return df


def get_raw_total_rows(path: str):
	"""Count logical CSV records robustly (handles quoted newlines). No caching."""
	try:
		with open(path, 'r', encoding='utf-8', newline='') as f:
			sample = f.read(4096)
			f.seek(0)
			try:
				dialect = csv.Sniffer().sniff(sample)
				f_has_header = csv.Sniffer().has_header(sample)
			except Exception:
				dialect = csv.excel
				f_has_header = True
			reader = csv.reader(f, dialect)
			rows = 0
			if f_has_header:
				next(reader, None)
			for _ in reader:
				rows += 1
			return int(rows)
	except Exception:
		return None


def get_decades(df):
	if 'decade' not in df.columns:
		return []
	decs = sorted(set(df['decade'].dropna().astype(str)))
	return decs


def main():
	# Inject custom CSS for neal.fun-inspired aesthetics
	st.markdown(
		"""
		<style>
		/* Import a clean, rounded font */
		@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

		html, body, [class^="css"]  {
		  font-family: 'Poppins', system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
		}

		/* Soft gradient background */
		.stApp {
		  background: radial-gradient(1200px 600px at 10% 10%, #17203a 0%, #0f1320 40%, #0b0f1a 100%);
		}

		/* Wider content and breathing room */
		.main .block-container {
		  max-width: 1200px;
		  padding-top: 2rem;
		}

		/* Hero section */
		.hero {
		  padding: 2.0rem 2.0rem;
		  border-radius: 18px;
		  background: linear-gradient(145deg, rgba(21,26,43,0.9), rgba(15,19,32,0.9));
		  border: 1px solid rgba(255,255,255,0.06);
		  box-shadow: 0 10px 30px rgba(0,0,0,0.35);
		}
		.hero h1 {
		  font-weight: 700;
		  letter-spacing: 0.3px;
		  margin: 0 0 0.5rem 0;
		}
		.hero p {
		  opacity: 0.85;
		  margin: 0;
		}


		/* Style metrics directly to avoid empty wrapper divs */
		div[data-testid="stMetric"] {
		  background: rgba(255,255,255,0.03);
		  border: 1px solid rgba(255,255,255,0.06);
		  border-radius: 16px;
		  padding: 1rem 1.25rem;
		}
		div[data-testid="stMetric"] label {
		  color: #cfd6e6 !important;
		  font-weight: 600;
		}

		/* Tabs as soft pills */
		.stTabs [data-baseweb="tab-list"] {
		  gap: 0.5rem;
		}
		.stTabs [data-baseweb="tab"] {
		  height: 44px;
		  background: rgba(255,255,255,0.04);
		  border-radius: 999px;
		  padding: 0 16px;
		  border: 1px solid rgba(255,255,255,0.06);
		}
		.stTabs [aria-selected="true"] {
		  background: linear-gradient(135deg, rgba(0,209,178,0.22), rgba(0,209,178,0.05));
		  border-color: rgba(0,209,178,0.35);
		}

		/* Hide default Streamlit footer */
		footer {visibility: hidden;}
		</style>
		""",
		unsafe_allow_html=True,
	)

	# Hero section with title and subtitle (single block to avoid empty divs)
	st.markdown(
		"""
		<div class="hero">
		  <h1>MovieMind</h1>
		  <p>Explore film and TV trends with a clean, playful dashboard — IMDb first, popularity next.</p>
		</div>
		""",
		unsafe_allow_html=True,
	)

	df = load_data()

	# Sidebar filters
	st.sidebar.header('Filters')
	theme = 'Dark'
	template = 'plotly_dark'
	type_value = st.sidebar.selectbox('Type', options=['MOVIE', 'SHOW', 'ALL'], index=2)
	decs = get_decades(df)
	if len(decs) >= 2:
		start_default = min(decs)
		end_default = max(decs)
		start = st.sidebar.selectbox('Start decade', options=decs, index=decs.index(start_default))
		end = st.sidebar.selectbox('End decade', options=decs, index=decs.index(end_default))
		decade_range = [start, end]
	else:
		decade_range = None

	# genre list from primary_genre or exploded genres
	all_genres = []
	if 'genres' in df.columns:
		for v in df['genres']:
			if isinstance(v, list):
				all_genres.extend(v)
			else:
				try:
					all_genres.extend(eval(v))
				except Exception:
					pass
	all_genres = sorted(set(all_genres))
	picked_genres = st.sidebar.multiselect('Genres', options=all_genres, default=[])

	# apply filters
	t = None if type_value == 'ALL' else type_value
	df_f = an.filter_data(df, type_value=t, decades=decade_range, genres=picked_genres)

	# KPI row
	col1, col2, col3 = st.columns([1,1,1])
	with col1:
		raw_path = os.path.join(ROOT, 'data', 'data.csv')
		if os.path.exists(raw_path):
			raw_total = get_raw_total_rows(raw_path)
		else:
			raw_total = None
		if raw_total is None:
			raw_total = len(df)
		st.metric(label='Total Titles (All)', value=f"{raw_total:,}")
	with col2:
		avg_imdb = float(df_f['imdb_score'].dropna().mean()) if 'imdb_score' in df_f.columns else 0
		st.metric(label='Avg IMDb Score', value=f"{avg_imdb:.2f}")
	with col3:
		if 'release_year' in df_f.columns and not df_f['release_year'].dropna().empty:
			yr_min, yr_max = int(df_f['release_year'].min()), int(df_f['release_year'].max())
			span = f"{yr_min} – {yr_max}"
		else:
			span = '—'
		st.metric(label='Year Range', value=span)

	# Optional second row for filtered count if you want clarity
	colf1, colf2, colf3 = st.columns([1,1,1])
	with colf1:
		st.metric(label='Titles (Filtered)', value=f"{len(df_f):,}")

	# Sidebar debug info to validate paths and counts
	with st.sidebar.expander('Data debug', expanded=False):
		try:
			raw_path_dbg = os.path.join(ROOT, 'data', 'data.csv')
			exists = os.path.exists(raw_path_dbg)
			st.write(f"raw path: {raw_path_dbg}")
			st.write(f"exists: {exists}")
			if exists:
				stat = os.stat(raw_path_dbg)
				st.write({
					"mtime": stat.st_mtime,
					"size_bytes": stat.st_size,
				})
				robust = get_raw_total_rows(raw_path_dbg)
				st.write({"csv_records_robust": robust})
				# Simple physical line count (header included)
				try:
					with open(raw_path_dbg, 'rb') as fh:
						lines = sum(1 for _ in fh)
					st.write({"physical_lines": int(lines)})
				except Exception:
					pass
				# Pandas row count for comparison
				try:
					p_rows = int(pd.read_csv(raw_path_dbg).shape[0])
					st.write({"pandas_rows": p_rows})
				except Exception as e:
					st.write({"pandas_error": str(e)})
			# Always show cleaned/filtered rows
			st.write({
				"cleaned_rows": int(len(df)),
				"filtered_rows": int(len(df_f)),
			})
		except Exception as e:
			st.write({"debug_error": str(e)})

	# Tabs
	tabs = st.tabs(['Overview', 'Genres', 'Ratings', 'Popularity', 'Countries', 'Map', 'Compare'])

	with tabs[0]:
		st.subheader('Overview')
		st.write('Number of titles (Movies and Shows or both) per decade.')
		tp = an.titles_per_decade(df_f)
		fig = vz.line_titles_per_decade(tp, template=template)
		st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

	with tabs[1]:
		st.subheader('Top Genres')
		tg = an.top_genres(df_f, n=10)
		fig = vz.bar_top_genres(tg, template=template)
		st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

		st.write('Click a bar and filter above for a simple drilldown table.')
		st.dataframe(df_f[['title', 'release_year', 'type', 'primary_genre', 'imdb_score']].head(25))

	with tabs[2]:
		st.subheader('Ratings (IMDb first)')
		hist = vz.hist_scores(df_f[['imdb_score']].dropna(), score_col='imdb_score', template=template)
		st.plotly_chart(hist, use_container_width=True, config={"displayModeBar": False})

		best = an.best_imdb_each_year(df_f)
		fig2 = vz.line_best_imdb_each_year(best, template=template)
		st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

	with tabs[3]:
		st.subheader('Popularity')
		top_pop = an.top_popular(df_f, n=20)
		fig = vz.bar_top_popular(top_pop, template=template)
		st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

	with tabs[4]:
		st.subheader('Countries (Production)')
		cc = an.country_counts(df_f)

		# Build friendly label: country full name only (no emoji)
		def country_label(v):
			try:
				if not isinstance(v, str):
					return str(v)
				code = v.strip().upper()
				rec = None
				if len(code) == 2 and code.isalpha():
					rec = pycountry.countries.get(alpha_2=code)
				elif len(code) == 3 and code.isalpha():
					rec = pycountry.countries.get(alpha_3=code)
				if rec is None:
					rec = pycountry.countries.get(name=code)
				return rec.name if rec else code
			except Exception:
				return str(v)

		cc = cc.copy()
		if 'country' in cc.columns:
			cc['label'] = cc['country'].apply(country_label)

		fig = vz.bar_top_countries(cc, template=template)
		st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

	with tabs[5]:
		st.subheader('World Map (Heatmap)')
		st.caption('A big, simple heatmap of production countries. Filter on the left to update it.')
		cc = an.country_counts(df_f)

		# Simple control for value scaling only
		scale_mode = st.radio('Scale', ['Log','Linear'], index=0, horizontal=True)

		map_fig = vz.choropleth_countries(
			cc,
			template=template,
			height=820,
			color_scale='Blues',
			scale_mode=scale_mode.lower(),
		)
		st.plotly_chart(map_fig, use_container_width=True, config={"displayModeBar": False})

	with tabs[6]:
		st.subheader('Compare IMDb vs TMDB')
		comp = an.imdb_vs_tmdb(df_f)
		color_by = 'type' if 'type' in comp.columns else None
		fig = vz.scatter_imdb_vs_tmdb(comp, color_by=color_by, template=template)
		st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


if __name__ == '__main__':
	main()

