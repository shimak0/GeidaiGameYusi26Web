const nav = document.querySelector(".site-nav");
const navToggle = document.querySelector(".nav-toggle");

if (nav && navToggle) {
  navToggle.addEventListener("click", () => {
    const isOpen = nav.classList.toggle("is-open");
    navToggle.setAttribute("aria-expanded", String(isOpen));
    navToggle.setAttribute("aria-label", isOpen ? "メニューを閉じる" : "メニューを開く");
  });

  nav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      nav.classList.remove("is-open");
      navToggle.setAttribute("aria-expanded", "false");
      navToggle.setAttribute("aria-label", "メニューを開く");
    });
  });
}

const optionalImages = [...document.querySelectorAll("[data-optional-image]")];

optionalImages.forEach((image) => {
  const handleMissingImage = () => {
    const fallbackSrc = image.dataset.fallbackSrc;
    if (fallbackSrc && !image.dataset.fallbackAttempted) {
      image.dataset.fallbackAttempted = "true";
      image.src = fallbackSrc;
      return;
    }
    image.hidden = true;
    image.closest(".gallery-item")?.remove();
  };

  image.addEventListener("error", handleMissingImage);
  if (image.complete && image.naturalWidth === 0) {
    handleMissingImage();
  }
});

window.addEventListener("load", () => {
  document.querySelectorAll("[data-optional-gallery]").forEach((gallery) => {
    if (!gallery.querySelector(".gallery-item")) {
      gallery.remove();
    }
  });
});

document.addEventListener("contextmenu", (event) => {
  if (event.target.closest("img")) event.preventDefault();
});

document.addEventListener("dragstart", (event) => {
  if (event.target.closest("img")) event.preventDefault();
});
