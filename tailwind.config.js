/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["templates/**/*.html", "./static/**/*.js", "./static/**/*.ts"],
    theme: {
        extend: {
            colors: {
                dark: {
                    DEFAULT: "#11151c",
                    100: "#151b25",
                    200: "#222c3d",
                },
            },
        },
    },
    plugins: [],
};
