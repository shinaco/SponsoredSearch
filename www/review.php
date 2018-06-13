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
	if (isset($_POST["Save"])){
		$prevrow = unserialize($_POST["vals"]);
		$query = $db->prepare('update searchresultsfinal set sameproduct = ?, sametype = ?, complement = ?, differentbrand = ?, notseller = ?, listingproduct = ?, listingvendors = ?, unavailable = ?, suspicious = ?, nonusdollar = ?, price = ?, shipping = ?, tofreeshipping = ?, othercost = ?, thirdparty = ?, unrelated = ?, comment = ? where City = ? and State = ? and Datetime = ? and SearchTerm = ? and GoogleURL = ? and AdURLWebsite = ? and WebsiteName = ? and Vendor = ? and PositionNum = ? and Position = ? and ResultConsistent = ? and PageNumber = ? and TypeofResult = ? and Comments = ? and AdValue = ? and StaticFilePath = ? and productName = ? and productID = ?');
		if(isset($_POST["sameproduct"])){
			$query->bindValue(1, 1);
		}
		else {
			$query->bindValue(1, 0);
		}
	    if(isset($_POST["sametype"])){
			$query->bindValue(2, 1);
		}
		else {
			$query->bindValue(2, 0);
		}
		if(isset($_POST["complement"])){
			$query->bindValue(3, 1);
		}
		else {
			$query->bindValue(3, 0);
		}
		if(isset($_POST["differentbrand"])){
			$query->bindValue(4, 1);
		}
		else {
			$query->bindValue(4, 0);
		}
		if(isset($_POST["listingproduct"])){
			$query->bindValue(5, 1);
		}
		else {
			$query->bindValue(5, 0);
		}
		if(isset($_POST["listingvendors"])){
			$query->bindValue(6, 1);
		}
		else {
			$query->bindValue(6, 0);
		}
		if(isset($_POST["notseller"])){
			$query->bindValue(7, 1);
		}
		else {
			$query->bindValue(7, 0);
		}
		if(isset($_POST["unavailable"])){
			$query->bindValue(8, 1);
		}
		else {
			$query->bindValue(8, 0);
		}
		if(isset($_POST["suspicious"])){
			$query->bindValue(9, 1);
		}
		else {
			$query->bindValue(9, 0);
		}
		if(isset($_POST["nonusdollar"])){
			$query->bindValue(10, 1);
		}
		else {
			$query->bindValue(10, 0);
		}
		if(!empty($_POST["price"])){
			$query->bindValue(11, $_POST["price"]);
		}
		else {
			$query->bindValue(11, null, SQLITE3_NULL);
		}
		if(!empty($_POST["shipping"])){
			$query->bindValue(12, $_POST["shipping"]);
		}
		else {
			$query->bindValue(12, null, SQLITE3_NULL);
		}
		if(!empty($_POST["tofreeshipping"])){
			$query->bindValue(13, $_POST["tofreeshipping"]);
		}
		else {
			$query->bindValue(13, null, SQLITE3_NULL);
		}
		if(!empty($_POST["othercost"])){
			$query->bindValue(14, $_POST["othercost"]);
		}
		else {
			$query->bindValue(14, null, SQLITE3_NULL);
		}
		if(!empty($_POST["thirdparty"])){
			$query->bindValue(15, $_POST["thirdparty"]);
		}
		else {
			$query->bindValue(15, null, SQLITE3_NULL);
		}
		if(!empty($_POST["unrelated"])){
			$query->bindValue(16, 1);
		}
		else {
			$query->bindValue(16,0);
		}
        if(!empty($_POST["comment"])){
			$query->bindValue(17, $_POST["comment"]);
		}
		else {
			$query->bindValue(17, null, SQLITE3_NULL);
		}
		for($i=0;$i<18;$i++){
			$query->bindValue($i+18, $prevrow[$i]);
		}
		$result=$query->execute();
	}
	/*$results = $db->query('SELECT * FROM searchresults as sr where not exists
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
sr.productID = srf.productID)');*/
	$disableprev = false;
	$disablenext = false;
	if (isset($_POST["curr"])){
		$curr = $_POST["curr"];
		if (isset($_POST["Prev"])){
			$curr=max($curr-1,1);
		}
		if (isset($_POST["Next"])){
			$curr++;
		}	
	}
	else{
		$curr = 1;
	}
	if($curr == 1){
		$disableprev = true;
	}
	$results = $db->query('SELECT * FROM searchresultsfinal');
	if($row = $results->fetchArray())
	{
		$cur = 1;
		while($cur<$curr){
			$cur++;
			if($row2 = $results->fetchArray()){
				$row = $row2;
			}
			else{
				$disablenext = true;
				$curr--;
				break;
			}
		}
		if (!$row2 = $results->fetchArray()){
			$disablenext = true;
		}
		$vals = serialize($row);
		$imgquery = $db->query("select * from products where productName = '{$row['productName']}' and productID = '{$row['productID']}'");
		$imgrow = $imgquery -> fetchArray();
?>
<form method="post" action="review.php">
<table border=1>
	<tr>
		<td colspan="2">Search Term:<br><?php echo $row['productName']; ?>
	</tr>
	<tr>
		<td width="25%"><img class="zoom" width="100%" src="<?php echo $imgrow['imageurl']; ?>"></td><td><a href=<?php echo $row["AdURLWebsite"] ?> target="_blank"><img class="zoom" width=100% src="<?php echo str_replace("file:///home/research/ResearchProject/GoogleSearch/data/","/images/",$row['StaticFilePath']); ?>" alt="test"></a></td>
	</tr>
	<tr>
		<td colspan = 2>
			<table><tr><td><input type="checkbox" name="sameproduct" value="1" <?php if ($row['sameproduct']==1) {?>checked="checked"<?php } ?>>same exact model</td>
				<td><input type="checkbox" name="sametype" value="1" <?php if ($row['sametype']==1) {?>checked="checked"<?php } ?>>same type (even if not same model)</td>
				<td><input type="checkbox" name="complement" value="1" <?php if ($row['complement']==1) {?>checked="checked"<?php } ?>>complement</td>
				<td><input type="checkbox" name="differentbrand" value="1" <?php if ($row['differentbrand']==1) {?>checked="checked"<?php } ?>>different brand</td>
                <td><input type="checkbox" name="notseller" value="1" <?php if ($row['notseller']==1) {?>checked="checked"<?php } ?>>not a seller</td>
                <td><input type="checkbox" name="unrelated" value="1" <?php if ($row['unrelated']==1) {?>checked="checked"<?php } ?>>unrelated</td>
                </tr>
				<tr><td><input type="checkbox" name="listingproduct" value="1" <?php if ($row['listingproduct']==1) {?>checked="checked"<?php } ?>>listing of products</td>
				<td><input type="checkbox" name="listingvendors" value="1" <?php if ($row['listingvendors']==1) {?>checked="checked"<?php } ?>>listing of vendors</td>
				<td><input type="checkbox" name="unavailable" value="1" <?php if ($row['unavailable']==1) {?>checked="checked"<?php } ?>>out of stock/unavailable</td>
				<td><input type="checkbox" name="suspicious" value="1" <?php if ($row['suspicious']==1) {?>checked="checked"<?php } ?>>suspicious</td>
					<td><input type="checkbox" name="nonusdollar" value="1" <?php if ($row['nonusdollar']==1) {?>checked="checked"<?php } ?>>Non US dollar</td>
                    <td>&nbsp;</td>
                </tr>
                <tr><td colspan=6>Comment: <input type="text" name="comment" value="<?php echo $row['comment']; ?>"></td></tr></table>
Price <input type="number" step=0.01 name="price" value="<?php echo $row['price']; ?>">
Shipping <input type="number" step=0.01 name="shipping" value="<?php echo $row['shipping']; ?>">
To free shipping <input type="number" step=0.01 name="tofreeshipping" value="<?php echo $row['tofreeshipping']; ?>">
Other Cost <input type="number" step=0.01 name="othercost" value="<?php echo $row['othercost']; ?>"><br>
Third party vendor<input type="text" name="thirdparty" value="<?php echo $row['thirdparty']; ?>">
			<input type="submit" name="Prev" value="Previous"<?php if($disableprev) { ?> disabled<?php } ?>>
			<input type="submit" name="Save" value="Save">
			<input type="submit" name="Next" value="Next"<?php if($disablenext) { ?> disabled<?php } ?>>
            <a href="index.php">Capture new data</a>
			<input type="hidden" name="curr" value='<?php echo $curr ?>'>
			<input type="hidden" name="vals" value='<?php echo $vals ?>'>
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
