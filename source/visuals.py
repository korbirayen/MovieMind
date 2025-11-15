import plotly.express as px
import plotly.graph_objects as go
import pycountry
import numpy as np


def bar_top_genres(df, template='plotly'):
	if df.empty:
		return px.bar(title='Top Genres (no data)')
	fig = px.bar(df, x='genre', y='count', title='Top Genres')
	fig.update_layout(template=template)
	return fig


def line_titles_per_decade(df, template='plotly'):
	if df.empty:
		return px.line(title='Titles per Decade (no data)')
	fig = px.line(df, x='decade', y='count', title='Titles per Decade')
	fig.update_layout(template=template)
	return fig


def hist_scores(df, score_col='imdb_score', template='plotly'):
	if df.empty:
		return px.histogram(title=f'{score_col} Distribution (no data)')
	fig = px.histogram(df, x=score_col, nbins=30, title=f'{score_col} Distribution')
	fig.update_layout(template=template)
	return fig


def bar_top_countries(df, template='plotly'):
	if df.empty:
		return px.bar(title='Top Production Countries (no data)')
	x_col = 'label' if 'label' in df.columns else 'country'
	fig = px.bar(df.head(20), x=x_col, y='count', title='Top Production Countries (Top 20)')
	fig.update_layout(template=template)
	return fig


def bar_top_popular(df, template='plotly'):
	if df.empty:
		return px.bar(title='Top Popular Titles (no data)')
	fig = px.bar(df, x='title', y='tmdb_popularity', color='release_year', title='Top Popular Titles')
	fig.update_layout(template=template, xaxis_tickangle=-45)
	return fig


def line_best_imdb_each_year(df, template='plotly'):
	if df.empty:
		return px.line(title='Best IMDb Each Year (no data)')
	fig = px.line(df, x='release_year', y='imdb_score', title='Best IMDb Each Year', markers=True)
	fig.update_traces(mode='lines+markers', hovertemplate='%{x}: %{y}')
	fig.update_layout(template=template)
	return fig


def scatter_imdb_vs_tmdb(df, color_by='type', template='plotly'):
	if df.empty:
		return px.scatter(title='IMDb vs TMDB (no data)')
	cols = ['imdb_score', 'tmdb_score']
	for c in cols:
		if c not in df.columns:
			return px.scatter(title='IMDb vs TMDB (missing columns)')
	if color_by in df.columns:
		fig = px.scatter(df.dropna(subset=cols), x='imdb_score', y='tmdb_score', color=color_by,
						 title='IMDb vs TMDB', opacity=0.7)
	else:
		fig = px.scatter(df.dropna(subset=cols), x='imdb_score', y='tmdb_score',
						 title='IMDb vs TMDB', opacity=0.7)
	fig.update_layout(template=template)
	return fig


def _iso2_to_iso3(code):
	try:
		if not isinstance(code, str) or len(code) == 0:
			return None
		c = pycountry.countries.get(alpha_2=code.upper())
		return c.alpha_3 if c else None
	except Exception:
		return None


def choropleth_countries(df_counts, template='plotly', height=720, color_scale='portland', scale_mode='log'):
	# expects columns: country (ISO2 or name), count
	if df_counts.empty:
		return go.Figure()
	if 'country' not in df_counts.columns or 'count' not in df_counts.columns:
		return go.Figure()

	# Map ISO2 -> ISO3 when possible
	iso3 = []
	for v in df_counts['country']:
		if isinstance(v, str) and len(v) in (2, 3):
			if len(v) == 2:
				iso3.append(_iso2_to_iso3(v))
			else:
				iso3.append(v.upper())
		else:
			# try name lookup
			try:
				rec = pycountry.countries.get(name=str(v))
				iso3.append(rec.alpha_3 if rec else None)
			except Exception:
				iso3.append(None)

	data = df_counts.copy()
	data['iso3'] = iso3
	data = data.dropna(subset=['iso3'])

	# choose value scaling
	if scale_mode and str(scale_mode).lower() == 'log':
		data['value'] = np.log1p(data['count'])
		colorbar_title = 'log1p(count)'
	else:
		data['value'] = data['count']
		colorbar_title = 'count'

	if data.empty:
		return go.Figure()

	fig = px.choropleth(
		data,
		locations='iso3',
		color='value',
		color_continuous_scale=color_scale,
		title='Production Countries (Heatmap)',
	)
	fig.update_coloraxes(colorbar_title=colorbar_title)
	fig.update_geos(showcoastlines=True, coastlinecolor="#888", showland=True, landcolor="#111" if 'dark' in template else "#f7f7f7")
	fig.update_layout(template=template, height=height, margin=dict(l=10, r=10, t=60, b=10))
	return fig

