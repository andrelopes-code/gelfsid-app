const path = require("path");

module.exports = {
    mode: "development",
    entry: "./static/ts/main.ts",
    output: {
        filename: "bundle.js",
        path: path.resolve(__dirname, "./static/ts/dist"),
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
