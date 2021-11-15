const json = (function () {
    var jsonData = null;
    $.ajax({
        'async': false,
        'global': false,
        'url': "/assets/plants.json",
        'dataType': "json",
        'success': function (data) {
            jsonData = data;
        }
    });
    return jsonData;
})();


$(document).ready(function(){
    $("#search").keyup(function(){
        $("div").each(function(){
            if ($(this).text().search(new RegExp(filter, "i")) < 0) {
                $(this).fadeOut();

            } else {
                $(this).show();
            }
        });
    })
});


function searchQuery() {
    // redirects to various result
    let location = document.location.pathname.substring(1).split(".")[0] // Location will be outside_concourse for example
    let query = document.getElementById("search__val").value;
    let items = json[location].filter(x => x.Name.toLowerCase().includes(query))
    if (items) {
        let listIndex = 0;
        for (let i = 0; i < items.length; i++) {
            let index = json[location].indexOf(items[i])
            if (document.location.hash == `#plant-${index}`) {
                listIndex = (i + 1) % items.length;
                break;
            }
        }
        let index = json[location].indexOf(items[listIndex])
        document.location.href = document.location.href.replace(document.location.hash,"") + `#plant-${index}`;
    }
    return false;
}
