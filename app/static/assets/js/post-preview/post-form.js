var showdown = require('showdown');

const converter = new showdown.Converter({strikethrough: true, emoji: true, tables: true});

const i_title_intro = document.getElementsByClassName('post-title-intro')[0]
const i_description_intro = document.getElementsByClassName('post-description-intro')[0]
const i_title_end = document.getElementsByClassName('post-title-end')[0]
const i_description_end = document.getElementsByClassName('post-description-end')[0]

const p_title_intro = document.getElementById('preview_title_intro');
const p_description_intro = document.getElementById('preview_description_intro');
const p_title_end = document.getElementById('preview_title_end');
const p_description_end = document.getElementById('preview_description_end');

i_title_intro.addEventListener('keyup', event =>{
    var value = event.target.value
    p_title_intro.innerHTML = converter.makeHtml(value);
})

i_description_intro.addEventListener('keyup', event=>{
    var value = event.target.value
    p_description_intro.innerHTML = converter.makeHtml(value);
})

i_title_end.addEventListener('keyup', event=>{
    var value = event.target.value
    p_title_end.innerHTML = converter.makeHtml(value)
})

i_description_end.addEventListener('keyup', event=>{
    var value = event.target.value
    p_description_end.innerHTML = converter.makeHtml(value)
})