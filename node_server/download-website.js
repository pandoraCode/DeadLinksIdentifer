const scrape = require('website-scraper');    // Requirement: npm install website-scraper

// Receiving parameters
if (process.argv.length == 4) {
  var url = process.argv[2];
  var dir = process.argv[3];
} else {
  console.error('\nPlease, type: node download-website.js <website_to_download> <directory_to_save_files>\n');
  process.exit(1);
}

let options = {
    urls: url,
    directory: dir,
};

// Downloading website
scrape(options).then((result) => {
    console.log("Website succesfully downloaded");
}).catch((err) => {
    console.log("An error ocurred", err);
});