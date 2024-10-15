import requests
import json
import pandas as pd
from dataclasses import dataclass
import matplotlib.pyplot as plt
from datetime import datetime
import os
import logging

logging.basicConfig(filename='report.txt', level=logging.INFO, format='%(message)s', filemode='w')
logger = logging.getLogger()


@dataclass()
class Graphics:
    """
    Genera los graficos segun los parametros y obtiene una fecha para guardarlos de forma clasificada.
    """

    def generate_from_df(self, title: str, type_graphics: str, name_file: str, data):
        """
        genera y guarda las graficas en formato png a partir de un data frame.

        :param title: titulo de la grafica.
        :param type_graphics: tipo de grafica.
        :param data_frame: data frame que se desea graficar.
        """
        data.plot(kind=type_graphics)

        plt.title(title)
        plt.xlabel('Año')
        plt.ylabel('Cantidad')

        root = self.get_root('graphics')
        plt.savefig(f'{root}/{name_file}.png')
        plt.close()

    def generate_a_vs_graphics(self, first_key: str, second_key: str, name_file: str, data: dict):
        """
        segun un diccionario que contiene dos tipos de registros, los separa y grafica para exportarlos a png.

        :param first_key: primera clave existente en el diccionario.
        :param second_key: segunda clave existente en el diccionario.
        :param name_file: nombre para guardar el archivo png.
        :param data: registros que se desean graficar.
        """
        years = list(data.keys())

        electric_values = [data[year][first_key] for year in years]
        combustion_values = [data[year][second_key] for year in years]

        plt.plot(years, electric_values, marker='o', label=first_key)
        plt.plot(years, combustion_values, marker='o', label=second_key)

        plt.title(f'{first_key} y {second_key}')
        plt.xlabel('Año')
        plt.ylabel('Cantidad')
        plt.legend()

        root = self.get_root('graphics')
        plt.savefig(f'{root}/{name_file}.png')
        plt.close()

    def get_root(self, first_root: str):
        """
        genera la fecha actual para crear y/o comprobar una ruta. si no existe la crea a partir de una ruta principal.

        :param first_root: ruta principal.
        :return: ruta que se genero desde la principal con la fecha anexada.
        """

        today = datetime.now().strftime("%Y/%m/%d/")
        split: list = today.split('/')

        root_save: str = first_root
        for root in split:

            if not os.path.exists(root_save):
                os.mkdir(root_save)

            root_save = f'{root_save}/{root}'
        return root_save


@dataclass()
class Main(Graphics):
    """
    Main class that executes the flow to obtain the records of the API, classify them, graph them and generate reports.
    """

    input_year: int

    total_rows: int = 0
    limit: int = 10000
    dict_electric = {}

    columns = ['combustible', 'anio_registro', 'departamento', 'municipio']
    headers = {'content-type': 'application/json'}
    url: str = 'https://www.datos.gov.co/resource/7qfh-tkr3.json'

    def send_request_gov(self, off_set: int):
        """
        Responsible method of making Get a Apis requests with param sql and pagination.

        :param off_set: determines from which point the record is taken.
        :return: response data from Api.
        """
        print(f'[INFO] init Main.send_request_gov. Batch = {int(off_set // self.limit)}')

        sql_query = (
            "select "
            "combustible, "
            "anio_registro, "
            "departamento, "
            "municipio "
            f"offset {off_set} "
            f"limit {self.limit}"
        )
        rsp = requests.request("GET", url=self.url, headers=self.headers, params={
            '$query': sql_query,
        })

        if rsp.status_code != 200:
            print('[ERROR] no fue posible consumir el Api')
            raise Exception

        try:
            response: list = json.loads(rsp.text)
        except:
            raise Exception

        return response

    def process_data_frame(self):
        """
        it obtains the answers from the API to generate a dataframe with the required columns and return the information.

        :return: data_frame Api gov.
        """
        print('[INFO] init Main.process_data_frame')

        off_set: int = 0
        data_frame = pd.DataFrame(columns=self.columns)

        while True:

            response_data: list = self.send_request_gov(off_set)
            len_response: int = len(response_data)

            if len_response == 0:
                break

            data_frame = pd.concat([data_frame, pd.DataFrame(response_data)], ignore_index=True)

            off_set += self.limit
            self.total_rows += len_response

        logger.info(f'Total de registros encontrados de la Api = {self.total_rows}')
        if self.total_rows == 0:
            raise Exception

        return data_frame

    def register_cars(self, data_frame):
        """
        Classifies all types of vehicles per year

        :param data_frame: data frame from api.
        :return: cars by years in data frame.
        """
        print('[INFO] init Main.register_cars')

        data_frame_year = data_frame[(data_frame['anio_registro'].astype(int) >= self.input_year)]
        count_by_year = data_frame_year.groupby('anio_registro').size()

        title: str = f'vehiculos registrados a partir del anio {self.input_year} = {data_frame_year.shape}'

        self.generate_from_df(title, 'bar', 'all_cars_by_year', count_by_year)
        del count_by_year

        logger.info(f'[INFO] {title}')
        return data_frame_year

    def electric_cars_in_year(self, data_frame_year):
        """
        responsible for grouping electric cars by year.

        : param data_frame_year: data frame filter by year.
        :return: new data frame.
        """
        print('[INFO] init Main.electric_cars_in_year')

        data_frame_electric = data_frame_year[(data_frame_year['combustible'] == 'ELECTRICO')]
        logger.info(f'\n\n[REQUERIMIENTO 1.1] Cantidad de vehiculos ELECTRICOS del anio '
                    f'{self.input_year} = {data_frame_electric.shape}')

        count_elecetric_by_year = data_frame_electric.groupby('anio_registro').size()
        self.dict_electric = count_elecetric_by_year.to_dict()

        title = f'cantidad de vehiculos ELECTRICOS por año'
        self.generate_from_df(title, 'line', 'all_electric_cars_by_year', count_elecetric_by_year)

        logger.info(f'\n\n[REQUERIMIENTO 2.1] Incremento de vehiculos ELECTRICOS por anio')
        last_value: int = 0
        logger.info(f'\t\t Anio Base {self.input_year} = {self.dict_electric[str(self.input_year)]}',
                    count_elecetric_by_year.to_dict())

        for year, value in self.dict_electric.items():
            incremental_sales: int = value - last_value
            logger.info(f'\t\t Porcentaje de incremento por anio {year} = {(incremental_sales / value) * 100} ')
            last_value = value

        del count_elecetric_by_year
        return data_frame_electric

    def department_and_municipality(self, df_electric_cars, data_frame):
        """
        It brings together the departments and municipalities to obtain the number of electric vehicles for each one.

        : param df_electric_cars: electric cars.
        : param data_frame: principal df.
        :return: None.
        """
        print('[INFO] init Main.department_and_municipality')

        data_frame_department = df_electric_cars.groupby('departamento').size()

        dict_department: dict = data_frame_department.to_dict()

        self.generate_from_df(title='electric cars in departments', type_graphics='bar',
                              name_file='electric_cars_in_departments', data=data_frame_department)
        del data_frame_department

        result_dep_city: dict = {}
        for department in dict_department:
            data_frame_city = data_frame[(data_frame['departamento'] == department)].groupby('municipio').size()
            dict_ciy: dict = data_frame_city.to_dict()

            result_dep_city[department] = {
                'total': dict_department[department],
                'municipios': dict_ciy
            }

        logger.info('\n\n[REQUERIMIENTO 2.2] Cantidad de vehiculos ELECTRICOS por DEPARTAMENTO y Municipio:')
        for department in result_dep_city:
            logger.info(f'\t - {department} total: {result_dep_city[department]["total"]}')
            for municipality, count in result_dep_city[department]['municipios'].items():
                logger.info(f'\t\t - {municipality} total: {count}')

    def combustible_cars(self, data_frame):
        """
        You get all the different electric vehicles to create a comparison per year.

        :param data_frame: principal df
        :return: None.
        """
        print('[INFO] init Main.combustible_cars')

        data_frame_comb = data_frame[(data_frame['combustible'] != 'ELECTRICO')]
        title = f'Vehiculos de COMBUSTION a partir del año {self.input_year} = {data_frame_comb.shape}'

        count_comb_by_year = data_frame_comb.groupby('anio_registro').size()
        self.generate_from_df(title, 'bar', 'all_combustion_cars_by_year', count_comb_by_year)

        dict_comb: dict = count_comb_by_year.to_dict()
        del count_comb_by_year

        actual_year: int = 2022
        year: int = self.input_year
        electric_and_comb: dict = {}
        while year <= actual_year:
            electric_and_comb[year] = {
                'COMBUSTION': dict_comb.get(str(year), 0),
                'ELECTRIC': self.dict_electric.get(str(year), 0),
            }
            year += 1

        self.generate_a_vs_graphics('ELECTRIC', 'COMBUSTION', 'electric_vs_comb', electric_and_comb)

        logger.info('\n\n[REQUERIMIENTO 2.3] Comparativa entre registro de vehiculos ELECTRICO vs COMBUSTION')
        for year in electric_and_comb:
            logger.info(f'\t - Anio {year}: ')
            logger.info(f'\t\t - Electrico total: {electric_and_comb[year]["ELECTRIC"]}')
            logger.info(f'\t\t - Combustible total: {electric_and_comb[year]["COMBUSTION"]}')

    def start_flow(self):
        """
        Inicia y controla el flujo del proceso.
        """
        data_frame = self.process_data_frame()

        df_cars_by_year = self.register_cars(data_frame)

        df_electric_cars = self.electric_cars_in_year(df_cars_by_year)
        del df_cars_by_year

        self.department_and_municipality(df_electric_cars, data_frame)
        del df_electric_cars

        self.combustible_cars(data_frame)


if __name__ == '__main__':
    year: int = 2019

    main_class: object = Main(year)
    main_class.start_flow()
