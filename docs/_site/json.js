
function getDomainVerdict() { 
    // e.preventDefault(); //prevent default action 
    var post_url = "https://cims.nyu.edu/~zc1245/cgi-bin/test2.cgi" //get form action url
    var request_method = "GET"; //get form GET/POST method
    var get_data = "domain=" + $("#searchString").val() //Creates new FormData object
    console.log(get_data);
    $.ajax({
        url : post_url,
        type: request_method,
        data : get_data,
	cache: false,
	error: function() {
            alert("script call was not successful");
        },
	success: function(data){
            console.log(data);
            $("#text").html(data["message"]);
        }
    })
};


$().ready(function(){

       $.ajax({
        type: "POST",
        url: "https://cims.nyu.edu/~zc1245/cgi-bin/test2.cgi", // URL of the Perl script

        // send firstname and name as parameters to the Perl script
        // data: "firstname=" + firstname + "&name=" + name,

        // script call was *not* successful
        error: function() { 
            alert("script call was not successful");
        }, 

        // script call was successful 
        // perl_data should contain the string returned by the Perl script 
        success: function(data){
            console.log("test connection with backend server... success")
	    console.log(data);
        }
      });   

    //$.getJSON("https://cims.nyu.edu/~zc1245/cgi-bin/test2.cgi", function( data ) {
    //console.log(data);
    //$("#text").html(data["status"]);
  //});
});
