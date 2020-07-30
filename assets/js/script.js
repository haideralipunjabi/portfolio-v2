const menu = document.querySelector(".menu");
const openMenuBtn = document.querySelector(".open-menu");
const closeMenuBtn = document.querySelector(".close-menu");
const menuLinks = document.querySelectorAll(".menu-link");
const navbar = document.getElementById("nav-bar");
const sticky = navbar.offsetTop;
const timelineButton = document.querySelector(".timeline-button");

const errorSpan = document.createElement('span');
errorSpan.textContent = "This field is required!"
errorSpan.classList.add('error')

window.onscroll = function shiftNav() {
  if (window.pageYOffset > sticky) {
    navbar.style.boxShadow = "0 2px 2px rgba(35,37,53,0.8)";
    navbar.style.height = "60px";
  } else {
    navbar.style.boxShadow = "none";
    navbar.style.height = "100px";
  }
};

openMenuBtn.addEventListener("click", openMenu);
closeMenuBtn.addEventListener("click", closeMenu);

menuLinks.forEach((link) => {
  link.addEventListener("click", closeMenu);
});

function openMenu() {
  document.body.classList.add("no-scroll");
  menu.classList.add("active");
  document.querySelector(".menu-links").classList.add("fade-down");
}

function closeMenu() {
  menu.classList.remove("active");
  document.body.classList.remove("no-scroll");
  document.querySelector(".menu-links").classList.remove("fade-down");
}

// contact form
const contactForm = document.getElementById("contact-form");
const formFields = document.querySelectorAll("#contact-form input, textarea")
formFields.forEach(field=>{
  field.addEventListener('focusout', ()=>{
    validateField(field);
  })
})
contactForm.addEventListener("submit", (e) => {
  e.preventDefault();
  let validate = true;
  let data = {};
  formFields.forEach(field=>{
    if(!validateField(field)){
      validate = false;
    }
    data[field.getAttribute('name')] = field.value;
  });
  if(validate){
    postData("/form/",data).then(res => {
      const message = document.getElementById("msg");
      if (res.status === 200) {
        message.style.display = "block";
        message.textContent = "Successfully send message!";
        formFields.forEach(field=>{
          field.value = "";
        })
        setTimeout(() => {
          message.style.display = "none";
        }, 10000);
      }
      
    })
  }
});


timelineButton.addEventListener('click',()=>{
    document.querySelector(".timeline").classList.toggle("timeline-collapsed");
  })

function validateField(field){
  if (field.nextElementSibling?.classList.contains('error')){
      field.parentElement.removeChild(field.nextElementSibling);
    }
    if(field.getAttribute('type')=='email'){
      if(!validateEmail(field.value)){
        field.parentElement.appendChild(errorSpan.cloneNode(true))
        return false;
      }
    }
    if(field.value.length == 0){
      field.parentElement.appendChild(errorSpan.cloneNode(true))
      return false;
    }
    return true;
}
function validateEmail(email) {
  let re =
    /^(([^<>()\[\]\.,;:\s@\"]+(\.[^<>()\[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/i;
  return re.test(String(email).toLowerCase());
}

async function postData(url = '', data = {}) {
  // Default options are marked with *
  const response = await fetch(url, {
    method: 'POST', // *GET, POST, PUT, DELETE, etc.
    mode: 'cors', // no-cors, *cors, same-origin
    cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
    credentials: 'same-origin', // include, *same-origin, omit
    headers: {
      'Content-Type': 'application/json'
      // 'Content-Type': 'application/x-www-form-urlencoded',
    },
    redirect: 'follow', // manual, *follow, error
    referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
    body: JSON.stringify(data) // body data type must match "Content-Type" header
  });
  return response.json(); // parses JSON response into native JavaScript objects
}

if ('serviceWorker' in navigator) {
  window.addEventListener('load', function () {
    navigator.serviceWorker.register('/sw.js').then(function (registration) {
      console.log('ServiceWorker registration successful with scope: ', registration.scope);
    }, function (err) {

      console.log('ServiceWorker registration failed: ', err);
    });
  });
}
window.addEventListener('beforeinstallprompt', (e) => {
  // Prevent the mini-infobar from appearing on mobile
  e.preventDefault();
  // Stash the event so it can be triggered later.

});
