document.addEventListener("DOMContentLoaded", function () {
    const speciesSelect = document.getElementById("species");
    if (!speciesSelect) return;

    new Choices(speciesSelect, {
        searchEnabled: true,
        searchPlaceholderValue: "Type to search species…",
        itemSelectText: "",
        shouldSort: true,
        placeholder: false
    });
});