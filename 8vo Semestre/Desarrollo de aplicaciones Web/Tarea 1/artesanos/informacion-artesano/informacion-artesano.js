const indice = localStorage.getItem('artesanoIndex');
const lcls = localStorage.getItem("artesanos");
const jsonArtesanos = JSON.parse(lcls); 

const infoArtesano = jsonArtesanos.artesanos[indice]

const nombre = document.getElementById('nombre');
const region = document.getElementById('region');
const comuna = document.getElementById('comuna');
const tipos = document.getElementById('tipos');
const fotos = document.getElementById('fotos');
const email = document.getElementById('email');
const celular = document.getElementById('celular');
const descripcion = document.getElementById('descripcion');

nombre.textContent = infoArtesano.nombre;
region.textContent = infoArtesano.region;
comuna.textContent = infoArtesano.comuna;
email.textContent = infoArtesano.email;

if (infoArtesano.celular === '') {
  celular.textContent = 'No hay datos';
  celular.style.color = 'red';
} else {
  celular.textContent = infoArtesano.celular;
}

if (infoArtesano.descripcion === '') {
  descripcion.textContent = 'No hay datos';
  descripcion.style.color = 'red';
} else {
  descripcion.textContent = infoArtesano.celular;
}

let tip = '';
infoArtesano.tipos.forEach(element => {
  tip += element + ', ';
});
tip = tip.slice(0, -2);
tip += '.'
tipos.textContent = tip;


