const path = require("path");

module.exports = {
    mode: "development",
    entry: "./src/static/js/main.ts",
    output: {
        filename: "bundle.js",
        path: path.resolve(__dirname, "src/static/js/dist"),
    },
    module: {
        rules: [
            {
                test: /\.ts$/,
                use: "ts-loader",
                exclude: /node_modules/,
            },
        ],
    },
    resolve: {
        extensions: [".ts", ".js"],
    },
};
