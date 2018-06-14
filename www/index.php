<html>
<body>
<style>
.zoom {
    transition: transform .2s; /* Animation */
    margin: 0 auto;
}

.zoom:hover {
    transform: scale(1.5); /* (150% zoom - Note: if the zoom is too large, it will go outside of the viewport) */
}
</style>
<?php
    
	$db = new SQLite3('/home/research/ResearchProject/GoogleSearch/data/googlesearch.db');
	if (isset($_POST["vals"])){
		$vals = unserialize(str_replace("&#39;","'",$_POST["vals"]));
		$query = $db->prepare('insert into searchresultsfinal values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)');
		for($i=0;$i<count($vals)/2;$i++){
			$query->bindValue($i+1, $vals[$i]);
		}
		if(isset($_POST["sameproduct"])){
			$query->bindValue(19, 1);
		}
		else {
			$query->bindValue(19, 0);
		}
		if(isset($_POST["sameproduct"])){
			$query->bindValue(19, 1);
		}
		else {
			$query->bindValue(19, 0);
		}
	    if(isset($_POST["sametype"])){
			$query->bindValue(20, 1);
		}
		else {
			$query->bindValue(20, 0);
		}
		if(isset($_POST["complement"])){
			$query->bindValue(21, 1);
		}
		else {
			$query->bindValue(21, 0);
		}
		if(isset($_POST["differentbrand"])){
			$query->bindValue(22, 1);
		}
		else {
			$query->bindValue(22, 0);
		}
		if(isset($_POST["listingproduct"])){
			$query->bindValue(23, 1);
		}
		else {
			$query->bindValue(23, 0);
		}
		if(isset($_POST["listingvendors"])){
			$query->bindValue(24, 1);
		}
		else {
			$query->bindValue(24, 0);
		}
		if(isset($_POST["notseller"])){
			$query->bindValue(25, 1);
		}
		else {
			$query->bindValue(25, 0);
		}
		if(isset($_POST["unavailable"])){
			$query->bindValue(26, 1);
		}
		else {
			$query->bindValue(26, 0);
		}
		if(isset($_POST["suspicious"])){
			$query->bindValue(27, 1);
		}
		else {
			$query->bindValue(27, 0);
		}
		if(isset($_POST["nonusdollar"])){
			$query->bindValue(28, 1);
		}
		else {
			$query->bindValue(28, 0);
		}
		if(!empty($_POST["price"])){
			$query->bindValue(29, $_POST["price"]);
		}
		else {
			$query->bindValue(29, null, SQLITE3_NULL);
		}
		if(!empty($_POST["shipping"])){
			$query->bindValue(30, $_POST["shipping"]);
		}
		else {
			$query->bindValue(30, null, SQLITE3_NULL);
		}
		if(!empty($_POST["tofreeshipping"])){
			$query->bindValue(31, $_POST["tofreeshipping"]);
		}
		else {
			$query->bindValue(31, null, SQLITE3_NULL);
		}
		if(!empty($_POST["othercost"])){
			$query->bindValue(32, $_POST["othercost"]);
		}
		else {
			$query->bindValue(32, null, SQLITE3_NULL);
		}
		if(!empty($_POST["thirdparty"])){
			$query->bindValue(33, $_POST["thirdparty"]);
		}
		else {
			$query->bindValue(33, null, SQLITE3_NULL);
		}
		if(!empty($_POST["unrelated"])){
			$query->bindValue(34, 1);
		}
		else {
			$query->bindValue(34,0);
		}
        if(!empty($_POST["comment"])){
			$query->bindValue(35, $_POST["comment"]);
		}
		else {
			$query->bindValue(35, null, SQLITE3_NULL);
		}
		$result=$query->execute()->finalize();
	}
	$results = $db->query('SELECT * FROM searchresults as sr where not exists
	(select 1 from searchresultsfinal as srf where sr.City = srf.City and
                                                sr.State = srf.State and
                                                sr.Datetime = srf.Datetime and
                                                sr.SearchTerm = srf.SearchTerm and
                                                sr.GoogleURL = srf.GoogleURL and
                                                sr.AdURLWebsite = srf.AdURLWebsite and
                                                sr.WebsiteName = srf.WebsiteName and
                                                sr.Vendor = srf.Vendor and
                                                sr.PositionNum = srf.PositionNum and
                                                sr.Position = srf.Position and
                                                sr.ResultConsistent = srf.ResultConsistent and
                                                sr.PageNumber = srf.PageNumber and
                                                sr.TypeofResult = srf.TypeofResult and
                                                sr.Comments = srf.Comments and
                                                sr.AdValue = srf.AdValue and
                                                sr.StaticFilePath = srf.StaticFilePath and 
sr.productName = srf.productName and
sr.productID = srf.productID)');
	
	if($row = $results->fetchArray())
	{
        $prevresults = $db->query('Select * from searchresultsfinal where AdURLWebsite = "' . $row['AdURLWebsite'] . '" order by Datetime desc');
        if($prevrow = $prevresults->fetchArray()){
            $prevres = true;
        }
        else {
            $prevres = false;
        }
        $file = fopen("/home/research/ResearchProject/GoogleSearch/data/products2.csv","r");
        while(! feof($file))
        {
            $arr=fgetcsv($file);
            if($arr[0]==$row['productID']){
                $img = $arr[2];
                break;
            }
        }
        //$imgquery = $db->query("select * from products where productName = '{$row['productName']}' and productID = '{$row['productID']}'");
        //$imgrow = $imgquery -> fetchArray();
?>
<form method="post" action="index.php">
<table border=1>
	<tr>
		<td colspan="2">Search Term: <?php echo $row['productName']; ?><br>City: <?php echo $row['City']; ?>, State: <?php echo $row['State']; ?>, Position: <?php echo $row['Position']; ?>, Page Number: <?php echo $row['PageNumber']; ?></td>
	</tr>
	<tr>
		<td width="25%"><img class="zoom" width="100%" src="<?php echo $img; ?>"></td><td><a href=<?php echo $row["AdURLWebsite"] ?> target="_blank"><img class="zoom" width=100% src="<?php echo str_replace("file:///home/research/ResearchProject/GoogleSearch/data/","/images/",$row['StaticFilePath']); ?>" alt="test"></a></td>
	</tr>
	<tr>
		<td colspan = 2>
			<table><tr><td><input type="checkbox" name="sameproduct" value="1"<?php if ($prevres && $prevrow['sameproduct'] == 1) { ?> checked="checked"<?php } ?>>same exact model</td>
				<td><input type="checkbox" name="sametype" value="1"<?php if ($prevres && $prevrow['sametype'] == 1) { ?> checked="checked"<?php } ?>>same type (even if not same model)</td>
				<td><input type="checkbox" name="complement" value="1"<?php if ($prevres && $prevrow['complement'] == 1) { ?> checked="checked"<?php } ?>>complement</td>
				<td><input type="checkbox" name="differentbrand" value="1"<?php if ($prevres && $prevrow['differentbrand'] == 1) { ?> checked="checked"<?php } ?>>different brand</td>
                <td><input type="checkbox" name="notseller" value="1"<?php if ($prevres && $prevrow['notseller'] == 1) { ?> checked="checked"<?php } ?>>not a seller</td>
                <td><input type="checkbox" name="unrelated" value="1"<?php if ($prevres && $prevrow['unrelated'] == 1) { ?> checked="checked"<?php } ?>>unrelated</td>
                </tr>
				<tr><td><input type="checkbox" name="listingproduct" value="1"<?php if ($prevres && $prevrow['listingproduct'] == 1) { ?> checked="checked"<?php } ?>>listing of products</td>
				<td><input type="checkbox" name="listingvendors" value="1"<?php if ($prevres && $prevrow['listingvendors'] == 1) { ?> checked="checked"<?php } ?>>listing of vendors</td>
				<td><input type="checkbox" name="unavailable" value="1"<?php if ($prevres && $prevrow['unavailable'] == 1) { ?> checked="checked"<?php } ?>>out of stock/unavailable</td>
				<td><input type="checkbox" name="suspicious" value="1"<?php if ($prevres && $prevrow['suspicious'] == 1) { ?> checked="checked"<?php } ?>>suspicious</td>
					<td><input type="checkbox" name="nonusdollar" value="1"<?php if ($prevres && $prevrow['nonusdollar'] == 1) { ?> checked="checked"<?php } ?>>Non US dollar</td>
                    <td>&nbsp;</td>
                </tr>
                <tr><td colspan=6>Comment: <input type="text" name="comment"<?php if ($prevres) { echo ' value="'. $prevrow['comment'] . '"'; } ?>></td></tr></table>
Price <input type="number" step=0.01 name="price"<?php if ($prevres) { echo ' value="'. $prevrow['price'] . '"'; } ?>>
Shipping <input type="number" step=0.01 name="shipping"<?php if ($prevres) { echo ' value="'. $prevrow['shipping'] . '"'; } ?>>
To free shipping <input type="number" step=0.01 name="tofreeshipping"<?php if ($prevres) { echo ' value="'. $prevrow['tofreeshipping'] . '"'; } ?>>
Other Cost <input type="number" step=0.01 name="othercost"<?php if ($prevres) { echo ' value="'. $prevrow['othercost'] . '"'; } ?>><br>
Third party vendor<input type="text" name="thirdparty"<?php if ($prevres) { echo ' value="' . $prevrow['thirdparty'] . '"'; } ?>>
			<input type="submit" value="Send">
            <a href="review.php">Review/Edit previous data</a>
			<input type="hidden" name="vals" value='<?php echo str_replace("'","&#39;",serialize($row)) ?>'>
			</td>
	</tr>
</table>
	</form>
<?php 
	}
	 else
	 {
	?>
	You have filled all the required information
	<?php
	 }
	?>
</body>
</html>
