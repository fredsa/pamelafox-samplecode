import com.google.gdata.client.maps.*;
import com.google.gdata.client.spreadsheet.*;
import com.google.gdata.data.*;
import com.google.gdata.data.maps.*;
import com.google.gdata.data.spreadsheet.*;
import com.google.gdata.data.maps.MapEntry;
import com.google.gdata.util.*;
import java.io.IOException;
import java.net.URL;

public class GetMapsFeed {
  
  public static void main(String[] args) {
   
	String username = "yourthing@gmail.com";
	String password = "yourpass";
	
	SpreadsheetService spreadsheetService = new SpreadsheetService("spreadsheetsaver");
    MapsService mapService = new MapsService("spreadsheetsaver");
    
    try {
      // Replace these credentials with your own
      spreadsheetService.setUserCredentials(username, password);
      mapService.setUserCredentials(username, password);
    } catch(AuthenticationException e) {
      System.out.println("Authentication Exception");
    }
    
      
    try {
      final URL listFeedUrl = new URL("http://spreadsheets.google.com/feeds/list/tVMGYp3zb1Ikx0Pqjea9KpA/od6/private/full");
      ListFeed feed = spreadsheetService.getFeed(listFeedUrl, ListFeed.class);
    	
      MapEntry mapEntry = createMap(mapService, feed);
      URL editUrl = mapEntry.getFeatureFeedUrl();
      convertSpreadsheet(mapService, editUrl, feed);
    } catch(ServiceException e) {
    	System.out.println("Service Exception" + e.getMessage() + e.getResponseBody());
    } catch(IOException e) {
    	System.out.println("I/O Exception");
    }
  }
  
  public static void convertSpreadsheet(MapsService mapService, URL editURL, ListFeed listFeed) 
     throws ServiceException, IOException {
	  
	  for (ListEntry entry : listFeed.getEntries()) {
		System.out.println(entry.getTitle().getPlainText());
	    CustomElementCollection columns = entry.getCustomElements();
	    String title = columns.getValue("title").replace("&", "&amp;");
	    String description = columns.getValue("description").replace("&", "&amp;");
	    String latitude = columns.getValue("latitude");
	    String longitude = columns.getValue("longitude");
	    String kml = "<Placemark>" +
	   "<name>" + title + "</name>" + 
       "<description>" + description + "</description>" + 
       "<Point>" + 
       "<coordinates>" + longitude + "," + latitude + ",0.0</coordinates>" + 
       "</Point></Placemark>";
	    System.out.println("KML" + kml + "KML");
	    createFeature(mapService, editURL, kml);
	  }
  }
  

  public static MapEntry createMap(MapsService myService, ListFeed listFeed)
    throws ServiceException, IOException {
	  final URL feedUrl = new URL("http://maps.google.com/maps/feeds/maps/default/full");
	  MapFeed resultFeed = myService.getFeed(feedUrl, MapFeed.class);
	  URL mapUrl = new URL(resultFeed.getEntryPostLink().getHref());
	    
	  // Create a MapEntry object
	  MapEntry myEntry = new MapEntry();
	  myEntry.setTitle(listFeed.getTitle());
	  myEntry.setSummary(new PlainTextConstruct("Exported from Spreasheet."));
	  Person author = new Person("Pamela Fox", null, "api.pamelafox@google.com");
	  myEntry.getAuthors().add(author);
	
	  return myService.insert(mapUrl, myEntry);
  }
  
  public static void createFeature(MapsService myService, URL editURL, String KML)
  	throws ServiceException, IOException {
	// Create a blank FeatureEntry object
	FeatureEntry featureEntry = new FeatureEntry();
	
	try {
	  // KML is simply XML so we'll use the XmlBlob object to store it
	  XmlBlob kml = new XmlBlob();
	  kml.setBlob(KML);
	  featureEntry.setKml(kml);
	} catch(NullPointerException e) {
	  System.out.println("Error: " + e.getClass().getName());
	}
	
	try {
	  // Insert the feature entry using the #post URL
	  myService.insert(editURL, featureEntry);
	} catch(ServiceException e) {
	  System.out.println("Error: " + e.getMessage());
	}
}
  
  
}