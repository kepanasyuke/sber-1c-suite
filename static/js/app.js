import { initPage } from "./pages.js";
import { initProductFilter, sortableTables } from "./components.js";

const page = document.body.dataset.page || "landing";

sortableTables();
initProductFilter();
initPage(page);
