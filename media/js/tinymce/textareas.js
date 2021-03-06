tinyMCE.init({
    mode : "textareas",
    theme : "advanced",
    theme_advanced_buttons1 : "undo,redo,charmap,search,replace,|,link,unlink,image,emotions,|,code,fullscreen",
    theme_advanced_buttons2 : "formatselect,fontsizeselect,bold,italic,underline,strikethrough,sub,sup,|,justifyleft,justifycenter,justifyright,justifyfull,outdent,indent,|,bullist,numlist,|,forecolor,backcolor,removeformat",
    theme_advanced_buttons3 : "",
    theme_advanced_toolbar_location : "top",
    theme_advanced_toolbar_align : "left",
    theme_advanced_path_location : "bottom",
    theme_advanced_resizing : true,
    browsers : "msie,gecko,opera,safari",
    dialog_type : "modal",
    entity_encoding : "raw",
    relative_urls : false,
    convert_urls : false,
    width : "800",
    height : "300",
    extended_valid_elements : "a[name|href|target|title],img[class|src|border=0|alt|title|hspace|vspace|width|height|align|name|style],hr[class|width|size|noshade],font[face|size|color|style],span[class|align|style]",
    advimage_update_dimensions_onchange: true,
    file_browser_callback : 'oiFileBrowser',
    plugins : "advimage,autosave,searchreplace,table,visualchars,advlink,emotions,media,style,template,xhtmlxtras,fullscreen",
    gecko_spellcheck : true,
    language : "tr"
});

function oiFileBrowser (field_name, url, type, win) {
    tinyMCE.activeEditor.windowManager.open({
        file : "/admin/upload/image/tinymce/",
        title : "File Browser",
        width : 300,
        height : 100,
        close_previous : "no"
    }, {
        window : win,
        input : field_name,
        resizable : "yes",
        inline : "yes",
    });
    return false;
}
