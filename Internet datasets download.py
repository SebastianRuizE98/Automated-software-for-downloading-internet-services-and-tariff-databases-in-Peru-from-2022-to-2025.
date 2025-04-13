from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import pandas as pd
import time


# Iniciar el navegador
driver = webdriver.Chrome()

def print_element_info(element, name):
    if element:
        print(f"{name} HTML: {element.get_attribute('outerHTML')}")
    else:
        print(f"{name} no encontrado.")

def is_siguiente_button_disabled(boton_siguiente):
    """ Verifica si el botón 'Siguiente' está deshabilitado. """
    try:
        # Verificar si está deshabilitado o si es invisible
        boton_siguiente_clase = boton_siguiente.get_attribute('class')
        if 'ui-state-disabled' in boton_siguiente_clase:
            return True
        return False
    except NoSuchElementException:
        return True

def is_table_updated(driver, last_data):
    """ Verifica si la tabla ha cambiado en esta página """
    tabla = driver.find_element(By.CSS_SELECTOR, "#gview_dataGrid > div.ui-jqgrid-bdiv")
    tabla_texto = tabla.text.strip()
    return tabla_texto != last_data

try:
    # Cargar la página
    url = "https://serviciosweb.osiptel.gob.pe/ConsultaSIRT/Buscar/frmConsultaTar.aspx"
    driver.get(url)


    # Esperar y hacer clic en el botón "Aceptar"
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "btnBv"))).click()

    # Esperar que los elementos se carguen
    time.sleep(2)  

    # Seleccionar vigencia de servicios

    # Seleccionar tipo de servicio
    campo_servicio = driver.find_element(By.XPATH, '//*[@id="IdddlServicio"]')
    campo_servicio.click()
    
    internet = driver.find_element(By.XPATH, '//*[@id="IdddlServicio"]/option[5]')
    internet.click()
    time.sleep(1)
    
   ###########################################

   # Clickear en el primer calendario
    calendario = WebDriverWait(driver, 3).until(
        EC.visibility_of_element_located((By.XPATH, '/html/body/form/table/tbody/tr[4]/td/table[1]/tbody/tr/td/div/table[1]/tbody/tr[8]/td[2]/table/tbody/tr[1]/td[2]/input[2]'))
    )
    
    # clickear en el calendario y evitar que sea interceptado
    try:
        calendario.click()
    except ElementClickInterceptedException:
            driver.execute_script("arguments[0].scrollIntoView();", calendario)
            calendario.click()  

    # Clickear en la primera fecha titular
    WebDriverWait(driver, 2).until(
         EC.element_to_be_clickable((By.XPATH, '/html/body/form/div[5]/div/div[1]/div[3]/div'))
    ).click()
    time.sleep(3)
    # Abrir primeras opciones de año
    # Esperar que el elemento antiguo desaparezca

    # Abrir las opciones de años
    WebDriverWait(driver, 2).until(
         EC.element_to_be_clickable((By.XPATH, '/html/body/form/div[5]/div/div[1]/div[3]/div'))
    ).click()

    # Abrir año 2022 en el primer calendario
    WebDriverWait(driver, 2 ).until(
         EC.element_to_be_clickable((By.XPATH, '/html/body/form/div[5]/div/div[2]/div[3]/table/tbody/tr[1]/td[4]/div'))
    ).click()
    time.sleep(3)

    # Abrir Enero

    WebDriverWait(driver, 2 ).until(
         EC.element_to_be_clickable((By.XPATH, '/html/body/form/div[5]/div/div[2]/div[2]/table/tbody/tr[1]/td[1]/div'))
    ).click()

    # Seleccionar primero de Enero
    WebDriverWait(driver, 2).until(
         EC.element_to_be_clickable((By.XPATH, '/html/body/form/div[5]/div/div[2]/div[1]/table/tbody/tr[1]/td[7]/div'))
    ).click()

    time.sleep(5)


    # Click en buscar
    driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[4]/td/div[1]/div[1]/img').click()


 # Comenzamos a interactuar con la tabla

    # Esperar a que el modal de carga desaparezca
    
    WebDriverWait(driver, 300).until(
       EC.invisibility_of_element_located((By.XPATH, '/html/body/div[3]'))
                )
    
    

    try:
        # Esperar a que el iframe esté presente y cambiar el contexto a él
        iframe = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "frmPanel"))
        )
        driver.switch_to.frame(iframe)
        print("Se cambió al iframe correctamente.")

        all_data = []
        last_data = ""

        while True:
            try:
                # Esperar a que la tabla esté visible dentro del iframe
                tabla = WebDriverWait(driver, 30).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "#gview_dataGrid > div.ui-jqgrid-bdiv"))
                )

                # Hacer scroll para asegurar que la tabla esté en el viewport
                driver.execute_script("arguments[0].scrollIntoView(true);", tabla)
                time.sleep(1)  # Breve pausa para que se rendericen los elementos

                # Obtener el contenido de la tabla
                tabla_texto = tabla.text.strip()
                if tabla_texto == "":
                    print("La tabla está vacía. Finalizando.")
                    break

                # Dividir por filas y extraer los datos
                filas = tabla_texto.split("\n")
                datos = [fila.split() for fila in filas]
                all_data.extend(datos)

                # Guardar los datos hasta el momento
                pd.DataFrame(all_data).to_excel("tabla_parcial.xlsx", index=False)

                # Verificar si la tabla cambió
                if not is_table_updated(driver, last_data):
                    print("La tabla no ha cambiado. Terminando la iteración.")
                    break
                last_data = tabla_texto

                # Intentar encontrar el botón "Siguiente"
                boton_siguiente = driver.find_element(By.XPATH, '/html/body/form/div[3]/div/div[5]/div/table/tbody/tr/td[2]/table/tbody/tr/td[6]/span')

                # Si el botón está deshabilitado o no cambia la tabla, terminamos
                if is_siguiente_button_disabled(boton_siguiente):
                    print("No hay más páginas. El botón 'Siguiente' está deshabilitado.")
                    break

                # Verificar si el botón es clickeable
                if not boton_siguiente.is_enabled():
                    print("Botón 'Siguiente' no clickeable. Terminando.")
                    break

                # Hacer scroll hasta el botón por si está fuera de vista
                driver.execute_script("arguments[0].scrollIntoView(true);", boton_siguiente)
                time.sleep(1)
                boton_siguiente.click()

                # Esperar un poco para asegurar que la tabla cambie
                time.sleep(1)

            except NoSuchElementException:
                print("Botón 'Siguiente' no encontrado. Fin de paginación.")
                break
            except ElementClickInterceptedException:
             print("No se pudo hacer clic en 'Siguiente'. Fin de paginación.")
             break
            except TimeoutException:
                print("Timeout esperando la tabla o el botón 'Siguiente'.")
                break

        # Guardar todo el contenido como DataFrame
        df_final = pd.DataFrame(all_data)
        print(df_final)

        df_final.to_excel('tabla_internet_todas_las_paginas.xlsx', index=False)

        
    except Exception as e:
        print(f"Error al extraer la fila: {e}")


finally:      
    
    driver.quit()






    

  
    

