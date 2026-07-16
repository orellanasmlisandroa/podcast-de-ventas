/* ============================================================
   Samira · Reportaje de nacimiento
   JavaScript puro (sin dependencias)

   Contiene:
   1. Datos y render de la galería
   2. Lightbox (abrir / cerrar / navegar con teclado y botones)
   3. Navegación "pegajosa" al hacer scroll
   4. Aparición progresiva de elementos (reveal)
   ============================================================ */

(function () {
  "use strict";

  /* ----------------------------------------------------------
     1 · GALERÍA
     Edita este array para cambiar fotos u orden.
     'src' = ruta de la imagen · 'alt' = texto accesible · 'caption' = pie
     ---------------------------------------------------------- */
  const PHOTOS = [
    { src: "img/samira-01.jpg", alt: "Samira dormida con turbante crema sosteniendo una flor", caption: "Primera flor" },
    { src: "img/samira-16.jpg", alt: "Samira envuelta en un arrullo rosa con lazo",              caption: "Bienvenida al mundo" },
    { src: "img/samira-06.jpg", alt: "Papá sosteniendo a Samira en la habitación",                caption: "En brazos de papá" },
    { src: "img/samira-04.jpg", alt: "Retrato del abuelo con Samira",                              caption: "El abrazo del abuelo" },
    { src: "img/samira-05.jpg", alt: "Retrato del abuelo con Samira en blanco y negro",           caption: "Generaciones" },
    { src: "img/samira-02.jpg", alt: "Detalle de las manitas y los pies de Samira",               caption: "Diez deditos" },
    { src: "img/samira-09.jpg", alt: "Mamá besando la frente de Samira en blanco y negro",        caption: "El beso de mamá" },
    { src: "img/samira-03.jpg", alt: "Papá mirando a Samira recién nacida",                       caption: "Primera mirada" },
    { src: "img/samira-07.jpg", alt: "Retrato cercano de Samira dormida",                          caption: "Sueño tranquilo" },
    { src: "img/samira-08.jpg", alt: "Retrato en blanco y negro de Samira en brazos",             caption: "Calma" },
    { src: "img/samira-10.jpg", alt: "Detalle del arrullo y el rostro de Samira",                 caption: "Detalles" },
    { src: "img/samira-11.jpg", alt: "Samira envuelta descansando",                                caption: "Descanso" },
    { src: "img/samira-12.jpg", alt: "Retrato de Samira recién nacida",                            caption: "Retrato" },
    { src: "img/samira-13.jpg", alt: "Momento tierno con Samira",                                  caption: "Ternura" },
    { src: "img/samira-14.jpg", alt: "Samira en su primer día",                                    caption: "Día uno" },
    { src: "img/samira-15.jpg", alt: "Retrato de familia con Samira",                              caption: "Familia" }
  ];

  const grid = document.getElementById("galleryGrid");

  // Construye cada figura de la galería a partir del array
  PHOTOS.forEach(function (photo, index) {
    const figure = document.createElement("figure");
    figure.className = "gallery-item reveal";
    figure.setAttribute("tabindex", "0");
    figure.setAttribute("role", "button");
    figure.setAttribute("aria-label", "Abrir foto: " + photo.caption);
    figure.dataset.index = index;

    const img = document.createElement("img");
    img.src = photo.src;
    img.alt = photo.alt;
    img.loading = "lazy";

    const caption = document.createElement("figcaption");
    caption.className = "gallery-item__caption";
    caption.textContent = photo.caption;

    figure.appendChild(img);
    figure.appendChild(caption);
    grid.appendChild(figure);
  });

  /* ----------------------------------------------------------
     2 · LIGHTBOX
     ---------------------------------------------------------- */
  const lightbox     = document.getElementById("lightbox");
  const lightboxImg  = document.getElementById("lightboxImg");
  const lightboxCap  = document.getElementById("lightboxCaption");
  const btnClose     = document.getElementById("lightboxClose");
  const btnPrev      = document.getElementById("lightboxPrev");
  const btnNext      = document.getElementById("lightboxNext");

  let currentIndex = 0;

  function showPhoto(index) {
    // Envuelve el índice para que sea circular
    currentIndex = (index + PHOTOS.length) % PHOTOS.length;
    const photo = PHOTOS[currentIndex];
    lightboxImg.src = photo.src;
    lightboxImg.alt = photo.alt;
    lightboxCap.textContent = photo.caption;
  }

  function openLightbox(index) {
    showPhoto(index);
    lightbox.classList.add("is-open");
    lightbox.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden"; // evita scroll de fondo
    btnClose.focus();
  }

  function closeLightbox() {
    lightbox.classList.remove("is-open");
    lightbox.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }

  // Abrir al hacer clic (o Enter/Espacio) en una figura de la galería
  grid.addEventListener("click", function (e) {
    const item = e.target.closest(".gallery-item");
    if (item) openLightbox(Number(item.dataset.index));
  });
  grid.addEventListener("keydown", function (e) {
    if (e.key === "Enter" || e.key === " ") {
      const item = e.target.closest(".gallery-item");
      if (item) { e.preventDefault(); openLightbox(Number(item.dataset.index)); }
    }
  });

  // Controles del lightbox
  btnClose.addEventListener("click", closeLightbox);
  btnNext.addEventListener("click", function () { showPhoto(currentIndex + 1); });
  btnPrev.addEventListener("click", function () { showPhoto(currentIndex - 1); });

  // Cerrar al hacer clic en el fondo oscuro (no sobre la imagen ni los botones)
  lightbox.addEventListener("click", function (e) {
    if (e.target === lightbox) closeLightbox();
  });

  // Teclado: Esc cierra, flechas navegan
  document.addEventListener("keydown", function (e) {
    if (!lightbox.classList.contains("is-open")) return;
    if (e.key === "Escape")      closeLightbox();
    if (e.key === "ArrowRight")  showPhoto(currentIndex + 1);
    if (e.key === "ArrowLeft")   showPhoto(currentIndex - 1);
  });

  // Deslizar (swipe) en móviles
  let touchStartX = 0;
  lightbox.addEventListener("touchstart", function (e) {
    touchStartX = e.changedTouches[0].screenX;
  }, { passive: true });
  lightbox.addEventListener("touchend", function (e) {
    const diff = e.changedTouches[0].screenX - touchStartX;
    if (Math.abs(diff) > 50) showPhoto(currentIndex + (diff < 0 ? 1 : -1));
  }, { passive: true });

  /* ----------------------------------------------------------
     3 · NAVEGACIÓN PEGAJOSA
     Cambia el fondo de la barra al desplazar la página.
     ---------------------------------------------------------- */
  const nav = document.querySelector(".nav");
  function onScroll() {
    if (window.scrollY > 60) nav.classList.add("is-scrolled");
    else nav.classList.remove("is-scrolled");
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ----------------------------------------------------------
     4 · REVEAL — aparición progresiva al hacer scroll
     ---------------------------------------------------------- */
  const revealEls = document.querySelectorAll(".reveal");

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealEls.forEach(function (el) { observer.observe(el); });
  } else {
    // Sin soporte: mostrar todo directamente
    revealEls.forEach(function (el) { el.classList.add("is-visible"); });
  }
})();
