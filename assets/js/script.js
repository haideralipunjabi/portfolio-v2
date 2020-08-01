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


timelineButton.addEventListener('click',()=>{
    document.querySelector(".timeline").classList.toggle("timeline-collapsed");
  })
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

document.getElementById("contact-form").addEventListener('submit',e=>{
  e.preventDefault();
  let name = document.getElementById("from_name").value;
  let email = document.getElementById("email").value;
  let msg = document.getElementById("message").value;
  const message = document.getElementById("msg");
  let data = encodeURI(`Name: ${name}\nEmail: ${email}\nMessage: ${msg}`)
  
  fetch(`/contact/${data}`, {
    'method': 'GET'
  }).then(r=>{
    if(r.status === 200){
      message.style.display = "block";
        message.textContent = "Successfully send message!";

        setTimeout(() => {
          message.style.display = "none";
        }, 10000);
    }
  })
})