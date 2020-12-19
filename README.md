![alt_text](/res/img/icon.jpg)   

## WaterQ

## Colombia IRCA Data Analysis

In this project, the analysis will be carried with the complete database for some municipalities of Colombia regarding water quality. Our goal is to do an analysis of the data existing in public data sources about water quality in Colombia and identify the main factors affecting the water quality results, allowing public organisms to have a wider knowledge about the problem so that they can deal with it more efficiently through public politics. We also include the information about mining extractions to find any relation between the data quality. And last but no least we provide a dashboard to help the final user of the information to navigate through the different tables, graphs and maps to take the best decision.

### Installing

To copy this repository locally run

```
git clone https://github.com/jquilismaluninorte/WaterQ.git
```

Once copy the repository, go to WaterQ folder on your command window and be sure to locate "requirements.txt", then run

```
pip install -r requirements.txt
```

#### Optional installing

To use session login, install Postgres and create a database named "waterq", and uncomment line 538 of app2.py file before run the application.

```
#db.create_all()
```

Replace your Postgres access password in line 562

```
passworddb='Your password'
```

The application create atomatically the table into database.

### Running the tests

Once installed all requirements, run this code on your commad window and wait to the program response:

```
python app2.py
```

After some seconds, the response looks like:

```
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:8050/ (Press CTRL+C to quit)
```

Then go to your browser an tipe this url [http://127.0.0.1:8050/](http://127.0.0.1:8050/) and the web page is rendered.

### Built With

- [Python](https://www.python.org/) - The programming language used.
- [Dash](https://pypi.org/project/dash/) - Python Framework for building ML & data science web apps.
- [Plotly](https://plotly.com/python/) - Plotly Python Open Source Graphing Library.

### Authors

- **Team 15 DS4A 2020** [WaterQ](https://agua.vatiolibre.com/)
- Laura Lucia García Mendoza
- Sandra Carolina Ropero Triana
- David Ricardo Vanegas Vargas
- Oscar Francisco Trujillo Puentes
- Sergio Alejandro Herrera Rivera
- Willian Javier Quilismal

### License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
