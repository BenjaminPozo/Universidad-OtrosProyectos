const displayButton = document.getElementById('displayButton');
const listaTipos = document.getElementById("tipo-artesania");
const selectRegion = document.getElementById('selectRegion');
const selectComuna = document.getElementById('selectComuna');
const icon = document.getElementById('icon');
const checkboxes = document.querySelectorAll('input[type="checkbox"]');

let selectedRegion = null;

var xhr = new XMLHttpRequest();
xhr.open("GET", "/get_data");

var jsonRegionComunas;

xhr.onreadystatechange = function() {
  if (xhr.readyState === 4 && xhr.status === 200) {
    var responseText = xhr.responseText;
    jsonRegionComunas = JSON.parse(responseText, function (key, value) {
      if (typeof value === 'string') {
        return decodeURIComponent(value);
      }
      return value;
    });
    
    selectRegion.addEventListener('change', function () {
      selectedRegion = this.options[selectRegion.selectedIndex].value;
      while (selectComuna.firstChild) {
          selectComuna.removeChild(selectComuna.firstChild);
      }
      cargarComunas(selectedRegion, jsonRegionComunas);
    });
    cargarComunas(selectedRegion, jsonRegionComunas);
  }
};
xhr.send();

function cargarComunas(selectedRegion, jsonRegionComunas){
  if (selectedRegion) {
    selectComuna.disabled = false;
    let comunas = null;
    for (const region in jsonRegionComunas.data) {
      if (region === selectedRegion) {
        comunas = jsonRegionComunas.data[region];
      }
    }

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
        let form = document.getElementById('artesano-form');
        form.submit();
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