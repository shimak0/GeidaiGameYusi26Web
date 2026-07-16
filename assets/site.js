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

const tryNextFallback = (image) => {
  const fallbackSources = (image.dataset.fallbackSrcs || image.dataset.fallbackSrc || "")
    .split(",")
    .map((source) => source.trim())
    .filter(Boolean);
  const fallbackIndex = Number(image.dataset.fallbackIndex || 0);
  if (fallbackIndex >= fallbackSources.length) return false;
  image.dataset.fallbackIndex = String(fallbackIndex + 1);
  image.src = fallbackSources[fallbackIndex];
  return true;
};

optionalImages.forEach((image) => {
  const handleMissingImage = () => {
    if (tryNextFallback(image)) return;
    image.hidden = true;
  };

  image.addEventListener("error", handleMissingImage);
  if (image.complete && image.naturalWidth === 0) {
    handleMissingImage();
  }
});

const loadCarouselImage = (image) =>
  new Promise((resolve) => {
    const finish = (isAvailable) => {
      image.removeEventListener("load", handleLoad);
      image.removeEventListener("error", handleError);
      resolve(isAvailable);
    };
    const handleLoad = () => finish(true);
    const handleError = () => {
      if (tryNextFallback(image)) return;
      finish(false);
    };

    image.addEventListener("load", handleLoad);
    image.addEventListener("error", handleError);
    if (image.complete) {
      if (image.naturalWidth > 0) {
        handleLoad();
      } else {
        handleError();
      }
    }
  });

document.querySelectorAll("[data-carousel]").forEach(async (carousel) => {
  const images = [...carousel.querySelectorAll(".carousel-image")];
  const dots = [...carousel.querySelectorAll("[data-carousel-dot]")];
  const placeholder = carousel.querySelector(".carousel-placeholder");
  const prevButton = carousel.querySelector("[data-carousel-prev]");
  const nextButton = carousel.querySelector("[data-carousel-next]");
  const availability = await Promise.all(images.map(loadCarouselImage));
  const availableImages = images.filter((_, index) => availability[index]);
  let currentIndex = 0;

  const render = () => {
    images.forEach((image) => {
      image.hidden = true;
    });
    dots.forEach((dot) => {
      dot.hidden = true;
      dot.classList.remove("is-active");
      dot.removeAttribute("aria-current");
      dot.disabled = true;
    });

    if (availableImages.length === 0) {
      placeholder.hidden = false;
      dots.slice(0, 3).forEach((dot, index) => {
        dot.hidden = false;
        dot.classList.toggle("is-active", index === 0);
      });
      prevButton.disabled = true;
      nextButton.disabled = true;
      return;
    }

    placeholder.hidden = true;
    availableImages[currentIndex].hidden = false;
    dots.slice(0, availableImages.length).forEach((dot, index) => {
      dot.hidden = false;
      dot.disabled = false;
      dot.classList.toggle("is-active", index === currentIndex);
      if (index === currentIndex) {
        dot.setAttribute("aria-current", "true");
      }
    });
    prevButton.disabled = availableImages.length < 2;
    nextButton.disabled = availableImages.length < 2;
  };

  prevButton.addEventListener("click", () => {
    currentIndex = (currentIndex - 1 + availableImages.length) % availableImages.length;
    render();
  });

  nextButton.addEventListener("click", () => {
    currentIndex = (currentIndex + 1) % availableImages.length;
    render();
  });

  dots.forEach((dot, index) => {
    dot.addEventListener("click", () => {
      if (index >= availableImages.length) return;
      currentIndex = index;
      render();
    });
  });

  render();
});

document.querySelectorAll("[data-youtube-embed]").forEach((iframe) => {
  const fallback = iframe.parentElement.querySelector(".youtube-fallback");
  if (window.location.protocol === "file:") {
    iframe.remove();
    fallback.hidden = false;
    return;
  }

  const embedUrl = new URL(iframe.dataset.youtubeEmbed);
  if (window.location.origin && window.location.origin !== "null") {
    embedUrl.searchParams.set("origin", window.location.origin);
  }
  embedUrl.searchParams.set("playsinline", "1");
  iframe.src = embedUrl.toString();
});

document.addEventListener("contextmenu", (event) => {
  if (event.target.closest("img")) event.preventDefault();
});

document.addEventListener("dragstart", (event) => {
  if (event.target.closest("img")) event.preventDefault();
});
