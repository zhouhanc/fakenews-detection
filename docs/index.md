
<script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>
<script src="/json.js"></script>
 

<div id="input">
         <input width="500" id="searchString" name="searchString"
                 placeholder="Search a domain (e.g.: nytimes.com)" type="text">
         <button id="submitbutton" name="googleSearchName" onclick="javascript:getDomainVerdict();">Search</button>
</div>

<div id="text"></div>

<script>
document.getElementById("text").innerHTML = "This domain is predicated to be: N/A";
</script>
