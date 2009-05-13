package guestbook;
import java.io.IOException;
import javax.servlet.http.*;

@SuppressWarnings("serial")
public class GuestbookServlet extends HttpServlet {
	public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
		response.setContentType("text/html");
		response.getWriter().println("<FONT SIZE=\"6\" FACE=\"courier\" COLOR=blue><MARQUEE WIDTH=100% BEHAVIOR=ALTERNATE BGColor=yellow> WELCOME TO MY WEB PAGE!!!</MARQUEE></FONT>");
	}
}
