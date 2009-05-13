package guestbook;

import java.io.IOException;
import java.util.Date;
import javax.jdo.PersistenceManager;
import javax.servlet.http.*;
import com.google.appengine.api.users.User;
import com.google.appengine.api.users.UserService;
import com.google.appengine.api.users.UserServiceFactory;
import java.util.Collections;
import javax.cache.Cache;
import javax.cache.CacheException;
import javax.cache.CacheFactory;
import javax.cache.CacheManager;


import guestbook.Greeting;
import guestbook.PMF;
import java.util.Properties;
import javax.mail.MessagingException;
import javax.mail.Message;
import javax.mail.Session;
import javax.mail.Transport;
import javax.mail.internet.AddressException; 
import javax.mail.internet.InternetAddress; 
import javax.mail.internet.MimeMessage; 
import java.net.MalformedURLException;
import java.net.URL;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;
import java.util.Random;

public class SignGuestbookServlet extends HttpServlet {
    public void doPost(HttpServletRequest req, HttpServletResponse resp)
                throws IOException {
        UserService userService = UserServiceFactory.getUserService();
        User user = userService.getCurrentUser();
        
        String content = req.getParameter("content");
        
        if (content.length() >= 500 ) {
        	content = content.substring(0, 499);
        }
        Date date = new Date();
        Greeting greeting = new Greeting(user, content, date);

        PersistenceManager pm = PMF.get().getPersistenceManager();
        try {
            pm.makePersistent(greeting);
        } finally {
            pm.close();
        }
        
        Cache cache;
        String key = "GREETINGS_CACHE";
        
        try {
	        CacheFactory cacheFactory = CacheManager.getInstance().getCacheFactory();
	        cache = cacheFactory.createCache(Collections.emptyMap());
	        cache.remove(key);
        } catch (CacheException e) {
        	// Log error
        }
        
        if (user != null) {
        	sendEmail(user.getEmail());
        }
        resp.sendRedirect("/inner.jsp");
    }
    
    public void sendEmail(String emailAddress) {

        Properties props = new Properties();
        Session session = Session.getDefaultInstance(props, null);

        try {
            Message msg = new MimeMessage(session);
            msg.setFrom(new InternetAddress("pamela.fox@gmail.com"));
            msg.addRecipient(Message.RecipientType.TO,
                             new InternetAddress(emailAddress));
            msg.setSubject("URGENT!! THIS IS NOT A HOAX");
            msg.setText(getRandomHoax());
            Transport.send(msg);
        } catch (AddressException e) {
            // ...
        } catch (MessagingException e) {
            // ...
        }
    }
    
    public String getRandomHoax() {
    	String[] hoaxFiles = { "aids-virus.txt", "victorias-secret-hoax.txt", "breast-cancer.txt", "ambercrombie-and-fitch-hoax.txt", "dave-matthews-hoax.txt", "save-the-horses.txt"};
    	
    	try {
    		Random random = new Random(); 
    		int randomPosition = random.nextInt(hoaxFiles.length);
            URL url = new URL("http://imagine-it.org/google/crapemails/" + hoaxFiles[randomPosition]);
            BufferedReader reader = new BufferedReader(new InputStreamReader(url.openStream()));
            String hoax = "";
            String line;

            while ((line = reader.readLine()) != null) {
            	hoax += line + "\n";
            }
            System.out.println(hoax);
            reader.close();
            return hoax;
        } catch (MalformedURLException e) {
            // ...
        } catch (IOException e) {
            // ...
        }
        return "RICK ROLL!";
    }
}