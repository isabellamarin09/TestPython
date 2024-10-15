## DEPENDENCIAS
    - pip install requests
    - pip install pandas
    - pip install matplotlib
    - pip install logging

## EXPLICACIÓN

### CLASE Main (Método principal)

    * start_flow: 
        controla el flujo del proceso, invoca a los demás métodos.
    * send_request_gov: 
        consume el Api publica, con un param de sql para obtener la data requerida en la query. Controla los codigos de estado y retorna el response en una lista de dicionarios.
    * process_data_frame: 
        llamado a send_request_gov de forma ciclica para recoger todas sus respuestas. Construye el dataframe con la información por cada ciclo y retorna el DF resultante.
    * register_cars: 
        Aplica un filtro que cuenta los carros registrados a partir de un año estipulado, retorna el data_frame con el filtro, grafica el resultado y envia al reporte.
    * electric_cars_in_year: 
        Aplica un filtro que agrupa y cuenta los carros registrados de tipo ELECTRICO a partir de un año estipulado, retorna el data_frame con el filtro, grafica el resultado y envia al reporte.
    * department_and_municipality: 
        Aplica un filtro que agrupa y cuenta por departamento y municipio los carros registrados de tipo ELECTRICO a partir de un año estipulado, retorna el data_frame con el filtro, grafica el resultado y envia al reporte.
    * combustible_cars: 
        Aplica un filtro que cuenta los carros registrados diferentes de ELECTRICO a partir de un año estipulado, para generar comparativa contra los de tipo ELECTRICO, retorna el data_frame con el filtro, grafica el resultado y envia al reporte.

### CLASE Graphics ()

    * generate_from_df: 
        Genera un PNG de grafica de un Data Frame, segun el tipo que se le indiqué, en una ruta estipulada.
    * generate_a_vs_graphics: 
        Genera un PNG de grafica de un Diccionario, que compara dos claves para hacer una comparativa, segun el tipo que se le indiqué, en una ruta estipulada.
    * get_root: 
        Genera la fecha actual para crear y/o comprobar una ruta. si no existe la crea a partir de una ruta principal.

### REPORTE

Contiene un traza de la información procesada, filtrada y depurada de los datos de Api,
con la finalida de generar un reporte detallado de los datos al momento de la ejecución.
A travez de un logger de tipo Info, se envia en cada método una insercción al archivo reporte.txt