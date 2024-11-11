const path = require("path");

module.exports = {
    mode: "development",
    entry: "./src/static/ts/main.ts",
    output: {
        filename: "bundle.js",
        path: path.resolve(__dirname, "src/static/ts/dist"),
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
