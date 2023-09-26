const indice = localStorage.getItem('hinchaIndex');
const lcls = localStorage.getItem("hinchas");
const jsonHinchas = JSON.parse(lcls); 

const infoHincha = jsonHinchas.hinchas[indice]

const nombre = document.getElementById('nombre');
const region = document.getElementById('region');
const comuna = document.getElementById('comuna');
const deportes = document.getElementById('deportes');
const transporte = document.getElementById('transporte');
const email = document.getElementById('email');
const celular = document.getElementById('celular');
const comentario = document.getElementById('comentario');

nombre.textContent = infoHincha.nombre;
region.textContent = infoHincha.region;
comuna.textContent = infoHincha.comuna;
transporte.textContent = infoHincha.transporte;
email.textContent = infoHincha.email;


if (infoHincha.celular === '') {
  celular.textContent = 'No hay datos';
  celular.style.color = 'red';
} else {
  celular.textContent = infoHincha.celular;
}

if (infoHincha.adicional === '') {
  comentario.textContent = 'No hay datos';
  comentario.style.color = 'red';
} else {
  comentario.textContent = infoHincha.adicional;
}

let dep = '';
infoHincha.deportes.forEach(element => {
  dep += element + ', ';
});
dep = dep.slice(0, -2);
dep += '.'
deportes.textContent = dep;
console.log(dep)
