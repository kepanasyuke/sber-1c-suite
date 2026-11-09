import { initPage } from "./pages.js";

const page = document.body.dataset.page || "landing";

initPage(page);
