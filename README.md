# MovieMind
Netflix style Movie Trend Analyzer
<hr>

#### How to Execute :
##### 1 / Execute in powershell or command line to clean data and save to cleaned.csv in data Folder
```powershell
python -c "from source.cleaning import clean_data, save_cleaned_data; df = clean_data(); save_cleaned_data(df, 'data/cleaned.csv')" 
```

##### 2 / Install and run the dashboard (Streamlit)

```powershell
pip install -r requirements.txt
streamlit run dashboard/app.py
```

The app loads `data/cleaned.csv`, and provides:
- Filters: type (MOVIE/SHOW/ALL), decade range, genre multi-select
- Tabs: Overview, Genres, Ratings, Popularity, Countries, Compare (later)
- Tabs: Overview, Genres, Ratings, Popularity, Countries, Map (big world heatmap), Compare
- Theme: Light/Dark toggle (affects Plotly charts)

