const path = require("path");

module.exports = {
    mode: "development",
    entry: {
        main: "./static/ts/main.ts",
        base: "./static/ts/base.ts",
    },
    output: {
        filename: "[name].js",
        path: path.resolve(__dirname, "./static/dist"),
    },
    module: {
        rules: [
            {
                test: /\.ts$/,
                use: "ts-loader",
                exclude: /node_modules/,
            },
            {
                test: /\.css$/i,
                use: ["style-loader", "css-loader"],
            },
        ],
    },
    resolve: {
        extensions: [".ts", ".js"],
    },
};
