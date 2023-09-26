import dataRegionesComunas from '../../region-comuna.json' assert { type: 'json' };

const displayButton = document.getElementById('displayButton');
const listaTipos = document.getElementById("tipo-artesania");
const selectRegion = document.getElementById('selectRegion');
const selectComuna = document.getElementById('selectComuna');
const icon = document.getElementById('icon')
let selectedRegion = null;

function cargarRegiones() {
  const optionNone = document.createElement('option');
  optionNone.value = '';
  optionNone.text = 'Selecciona una Región'
  selectRegion.appendChild(optionNone)
    dataRegionesComunas.regiones.forEach(region => {
        const option = document.createElement('option');
        option.value = region.region;
        option.text = region.region;

        selectRegion.appendChild(option);
    });
}

function cargarComunas(selectedRegion) {
    if (selectedRegion) {
        selectComuna.disabled = false;
        let comunas = null;
        dataRegionesComunas.regiones.forEach(region => {
            if (region.region === selectedRegion) {
                comunas = region.comunas;
            }
        });
        const optionNone = document.createElement('option');
        optionNone.text = 'Selecciona una comuna';
        optionNone.value = '';
        selectComuna.appendChild(optionNone);
        comunas.forEach(comuna => {
            const option = document.createElement('option');
            option.value = comuna;
            option.text = comuna;

            selectComuna.appendChild(option);
        });
    } else {
        const option = document.createElement('option');
        option.text = 'Selecciona una región';
        option.value = '';
        selectComuna.appendChild(option);

        selectComuna.disabled = true;
    }
}

displayButton.addEventListener('click', (event) => {
    event.preventDefault();
    if (listaTipos.style.display === 'none') {
        icon.className = "material-symbols-outlined";
        icon.textContent = "expand_less";
        listaTipos.style.display = 'block';
    } else {
        icon.className = "material-symbols-outlined";
        icon.textContent = "expand_more";
        listaTipos.style.display = 'none';
    }
});

selectRegion.addEventListener('change', function () {
    selectedRegion = this.options[selectRegion.selectedIndex].value;
    while (selectComuna.firstChild) {
        selectComuna.removeChild(selectComuna.firstChild);
    }
    cargarComunas(selectedRegion);
});

cargarRegiones();
cargarComunas(selectedRegion);

const checkboxes = document.querySelectorAll('input[type="checkbox"]');

checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', () => {
        const seleccionados = document.querySelectorAll('input[type="checkbox"]:checked');
        if (seleccionados.length >= 3) {
            checkboxes.forEach(checkbox => {
                if (!checkbox.checked) {
                    checkbox.disabled = true;
                }
            });
            listaTipos.style.display = 'none'
        } else {
            checkboxes.forEach(checkbox => {
                checkbox.disabled = false;
            });
        }
    });
});

const validarArtesano = () => {

  function validarEmail(email) {
    if (email) {
      const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
      return emailRegex.test(email);
    } else {
      return false;
    }
  }

  function validarNombre(nombre) {
    if (nombre) {
      if (nombre.length < 3 || nombre.length > 80) {
        return false;
      } else {
        return true
      }
    } else {
      return false;
    }
  }

  function validarCelular(celular) {
    if (celular) {
      const celularSinEspacios = celular.replace(/\s+/g, "");
      const celularRegex = /^\+569\d{8}$/;
      return celularRegex.test(celularSinEspacios)
    } else {
      return true
    }
  }

  function validarFotos(fotos) {
    if (!fotos) return false;

    let lengthValid = 1 <= fotos.length && fotos.length <= 3;

    let typeValid = true;

    for (const foto of fotos) {
      let fotoFamily = foto.type.split('/')[0];
      typeValid = typeValid && fotoFamily === "image";
    }

    return lengthValid && typeValid;
  }
  
  let nombreInput = document.getElementById("nombre");
  let emailInput = document.getElementById("email");
  let fotosInput = document.getElementById("fotos");
  let celularInput = document.getElementById("celular");
  let descripcionInput = document.getElementById("descripcion");

  let isValid = false;
  let msg = "";

  const seleccionados = document.querySelectorAll('input[type="checkbox"]:checked');
  if (seleccionados.length < 1 || seleccionados.length > 3) {
      msg += "Tipo de artesanías, "
  }

  if (!validarNombre(nombreInput.value)) {
    msg += "Nombre, ";
    nombreInput.style.borderColor = "Red";
  } else {
    nombreInput.style.borderColor = "";
  }

  if (selectRegion.value === "") {
    msg += "Región, ";
    selectRegion.style.borderColor = "Red";
  } else {
    selectRegion.style.borderColor = "";
  }

  if (selectComuna.value === "") {
    msg += "Comuna, ";
    selectComuna.style.borderColor = "Red";
  } else {
    selectComuna.style.borderColor = "";
  }

  if (!validarEmail(emailInput.value)) {
    msg += "Email, ";
    emailInput.style.borderColor = "Red";
  } else {
    emailInput.style.borderColor = "";
  }

  if (!validarCelular(celularInput.value)) {
    msg += "Celular, ";
    celularInput.style.borderColor = "Red";
  } else {
    celularInput.style.borderColor = "";
  }

  if (!validarFotos(fotosInput.files)) {
    msg += "Fotos, ";
  }

  if (msg === "") {
    msg = "Artesano agregado con éxito";
    isValid = true;
  } else {
    msg = msg.slice(0, -2);
    msg += '.'
  }
  
  if (isValid) {
    Swal.fire({
      title: '¿Confirma el registro de este artesano?',
      icon: 'question', 
      showCancelButton: true,
      confirmButtonText: 'Si, confirmo',
      cancelButtonText: 'No, volver al formulario'
    }).then((result) => {
      if (result.isConfirmed) {
        const tiposSeleccionados = [];
        seleccionados.forEach(tipo => {
          tiposSeleccionados.push(tipo.value)
        })
        
        const nombre = nombreInput.value;
        const email = emailInput.value;
        const celular = celularInput.value;
        const region = selectRegion.value;
        const comuna = selectComuna.value;
        const descripcion = descripcionInput.value;
        const fotos = fotosInput.files;
        

        const artesano = {
          "tipos": tiposSeleccionados,
          "nombre": nombre,
          "email": email,
          "celular": celular,
          "region": region,
          "comuna": comuna,
          "fotos": fotos,
          "descripcion": descripcion
        }    

        let artesanos = localStorage.getItem("artesanos")
        if (artesanos) {
          const artesanosJson = JSON.parse(artesanos);
          artesanosJson.artesanos.push(artesano);
          const artesanosLocal = JSON.stringify(artesanosJson);
          localStorage.setItem("artesanos", artesanosLocal);
        } else {
          let artesanosJson = {
            "artesanos" : [artesano]
          }
          const artesanosLocal = JSON.stringify(artesanosJson);
          localStorage.setItem("artesanos", artesanosLocal);
        }

        Swal.fire({
          title: 'Hemos recibido el registro de Artesano. Muchas gracias',
          icon: 'success', 
          confirmButtonText: 'Ok',
        }).then((result2) => {
          if (result2.isConfirmed) {
            window.location.href = '../../index.html';
          }
        })
      }
    });
  } else {
    Swal.fire({
      title: 'Se detectaron errores en los siguientes campos:',
      text: msg,
      icon: 'error',
      confirmButtonText: 'Ok'
    });
  }
}
let submitBtn = document.getElementById("enviarForm");
submitBtn.addEventListener("click", validarArtesano);