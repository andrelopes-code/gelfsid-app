/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["templates/**/*.html", "./static/**/*.js", "./static/**/*.ts"],
    theme: {
        extend: {
            colors: {
                primary: "var(--primary-color)",
                secondary: "var(--secondary-color)",
                dark: {
                    DEFAULT: "var(--dark)",
                    100: "var(--dark-100)",
                    200: "var(--dark-200)",
                },
            },
        },
    },
    plugins: [],
};
