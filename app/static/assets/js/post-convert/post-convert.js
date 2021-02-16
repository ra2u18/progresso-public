var showdown = require('showdown');

var converter = new showdown.Converter({strikethrough: true, emoji: true, tables: true});

const d_description_intro = document.getElementById('project-description-intro')
const d_description_end = document.getElementById('project-description-end')

d_description_intro.innerHTML = `${converter.makeHtml(g_description_intro)}`
d_description_end.innerHTML = `${converter.makeHtml(g_description_end)}`
