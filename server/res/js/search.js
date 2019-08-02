var postParams;
var isArticles = true;
var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

$.ajax({
    url: "https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyBxDK6uZ7vUJ7Q0T1UXmh7NZovDErHBERI",
    method: "POST",
    success: function (success) {
        postParams = {lat: success.location.lat, long: success.location.lng};
    },
    error: function (req,err) {
        postParams = {lat: "43.082853", long: "-77.675906"};
    },
    async: false
});

$().ready(function () {
    var searchtext = findGetParameter('searchbox');

    if (searchtext !== null){
        window.history.replaceState({}, document.title, "/view/search.html");
        $('#searchbox').val(searchtext);
        $('#homesearch').trigger('click');
    }
});

$("#sample-images").click(function () {
    $("#image-tab").trigger('click');
});

$("#article-tab").click(function () {
    isArticles = true;
    if (!$("#article-tab").hasClass("active")) {
        $("#article-tab").addClass("active");
        $("#image-tab").removeClass("active");
        searchAjax();
    }
});

$("#image-tab").click(function () {
    isArticles = false;
    if (!$("#image-tab").hasClass("active")){
        $("#image-tab").addClass("active");
        $("#article-tab").removeClass("active");
        searchAjax();
    }
});

$("#homesearch").click(function () {
    postParams['searchbox'] = $("#searchbox").val();
    console.log(postParams);
    searchAjax();
});

function searchAjax() {
    $('#listing').empty();
    $('#extra').hide();

    $.post({
        url: "/search",
        data: postParams,
        dataType: 'json',
        success: function (success) {
            console.log(success);
            populate(success);
        },
        error: function (req,err) {
            console.log(err)
        },
        async: false
    })
}

function populate(data) {
    var body = $('#listing');
    var stats = $("#statistics");
    var extra = $("#extra");

    if (isArticles) {
        data['data'].forEach(function (article) {
            var div = $("<div class='item' id='"+article['id']+"'></div>");

            var a = $("<a target='_blank' href='"+article['readMoreUrl']+"'> </a>");

            $("<div class='title'>"+article['title']+"</div>").appendTo(a);
            if (article['readMoreUrl'] != null)
                $("<div class='url'>"+article['readMoreUrl']+"</div>").appendTo(a);
            else
                $("<div class='url'>"+article['url']+"</div>").appendTo(a);

            a.appendTo(div);

            $("<div class='content'>"+article['content']+"</div>").appendTo(div);
            if('comments' in article)
                article['comments'].forEach(function (comment) {
                    var date = new Date(comment['timestamp']);
                    $("<div class='comment'>"+comment['content']+" - <span class='user'>"+(date.getDate()+" "+months[date.getMonth()]+" "+date.getFullYear()+" at "+date.getHours()+":"+(date.getMinutes()<10?'0'+date.getMinutes():date.getMinutes()))+"</span></div>").appendTo(div);
                });
            $("<a class='add-comment' onclick='addComment("+article['id']+")'>add comment</a>").appendTo(div);

            body.append(div);
        });

        var div = $("#sample-images");
        div.empty();

        let limit = Math.min(4,data['data'].length);
        if(limit%2===1)
            limit-=1;
        var row = $("<div class='snap-row'></div>");
        for(let i=0;i<limit;i++){
            console.log(limit);
            if(i%2===0 && i!==0) {
                div.append(row);
                row = $("<div class='snap-row'></div>");
            }
            $("<img class='snap-col' src='/api/image/"+data['data'][i]['id']+"' />").appendTo(row);
        }
        div.append(row);

        stats.empty();

        $("<h3>Statistics</h3>").appendTo(stats);

        $("<p><b>Articles retrieved: </b>"+data["data"].length+"</p>").appendTo(stats);
        $("<p><b>Time taken: </b>"+data["time"]+" milliseconds</p>").appendTo(stats);
        if("ip" in data)
            $("<p><b>User IP address: </b>"+data["ip"]+"</p>").appendTo(stats);
        if("loc" in data)
            $("<p><b>User location: </b>"+data["loc"]["lat"]+", "+data['loc']['long']+"</p>").appendTo(stats);
        $("<p><b># of images stored: </b>"+data["images"]+"</p>").appendTo(stats);


        if (limit==0)
            div.hide();

        extra.show();
    }else {
        extra.hide();
        data['data'].forEach(function (article) {
            if (article['readMoreUrl'] != null)
                var link = article['readMoreUrl'];
            else
                var link = article['url'];

            var div = $("<a target='_blank' class='frame' href='"+link+"' id='"+article['id']+"'></a>");
            $("<img src='/api/image/"+article['id']+"' />").appendTo(div);
            $("<div class='title'>"+article['title']+"</div>").appendTo(div);

            $("<div class='url'>"+link+"</div>").appendTo(div);

            body.append(div);
        });
    }
}

function addComment(id) {
    var item = $('#'+id);
    item.children().last().remove();

    var row = $("<div style='margin-top: 5px'></div>");
    var input = $("<input class='commentbox' type='search' placeholder='Comment here...' required>");
    var button = $("<input class='commentbutton' type='submit' value='Submit'>");

    button.click(function () {
       $.post({
           url: "/api/article/"+id+"/comment",
           data: {comment:input.val()},
           success: function (success) {
               item.children().last().remove();
               $("<div class='comment'>"+input.val()+" - <span class='user'>just now</span></div>").appendTo(item);
               $("<a class='add-comment' onclick='addComment("+id+")'>add comment</a>").appendTo(item);
           }
       })
    });
    input.appendTo(row);
    button.appendTo(row);

    item.append(row);
}

function findGetParameter(parameterName) {
    var result = null,
        tmp = [];
    location.search
        .substr(1)
        .split("&")
        .forEach(function (item) {
            tmp = item.split("=");
            if (tmp[0] === parameterName) result = decodeURIComponent(tmp[1]);
        });
    if (result==null) return result;
    return result.replace(/[+]/g, ' ');
}