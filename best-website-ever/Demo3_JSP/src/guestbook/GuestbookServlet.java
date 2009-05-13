package guestbook;
import java.io.IOException;
import javax.servlet.http.*;
import com.google.appengine.api.users.User;
import com.google.appengine.api.users.UserService;
import com.google.appengine.api.users.UserServiceFactory;


@SuppressWarnings("serial")
public class GuestbookServlet extends HttpServlet {
	public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
		response.setContentType("text/html");
		
		UserService userService = UserServiceFactory.getUserService();
	    User user = userService.getCurrentUser();
	    String thisURL = request.getRequestURI();
	  
		if (user != null) {
			response.getWriter().println("<FONT SIZE=\"6\" FACE=\"courier\" COLOR=blue><MARQUEE WIDTH=100% BEHAVIOR=ALTERNATE BGColor=yellow> WELCOME TO MY WEB PAGE, " + user.getNickname() + "!!!</MARQUEE></FONT>");
			response.getWriter().println("<blink><a href=\"" + userService.createLogoutURL(thisURL) + "\">Sign out</a></blink>");
		} else {
			response.getWriter().println("<FONT SIZE=\"6\" FACE=\"courier\" COLOR=blue><MARQUEE WIDTH=100% BEHAVIOR=ALTERNATE BGColor=yellow> WELCOME TO MY WEB PAGE!!!</MARQUEE></FONT>");
			response.getWriter().println("<blink><a href=\"" + userService.createLoginURL(thisURL) + "\">Sign in</a></blink>");
        }
	}
}
