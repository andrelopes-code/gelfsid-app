(function () {
    function replaceCommaWithDot() {
        const inputFields = document.querySelectorAll('input[type="text"].numeric-field');

        inputFields.forEach(function (field) {
            field.addEventListener("blur", function () {
                if (field.value) {
                    field.value = field.value.replace(",", ".");
                }
            });
        });
    }

    window.addEventListener("load", replaceCommaWithDot);
})();
