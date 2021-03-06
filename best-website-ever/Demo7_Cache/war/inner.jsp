<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ page import="java.util.List" %>
<%@ page import="javax.jdo.PersistenceManager" %>
<%@ page import="com.google.appengine.api.users.User" %>
<%@ page import="com.google.appengine.api.users.UserService" %>
<%@ page import="com.google.appengine.api.users.UserServiceFactory" %>
<%@ page import="guestbook.Greeting" %>
<%@ page import="guestbook.PMF" %>

<html>
  <body>
  <center>
 <img src="/images/anicat9.gif"><img src="/images/hamsterdance2.gif"><img src="/images/dozer.gif"><img src="/images/hamsterdance2.gif"> <img src="/images/anicat9.gif">
 </center>
<%
    UserService userService = UserServiceFactory.getUserService();
    User user = userService.getCurrentUser();
    if (user != null) {
%>
	<FONT SIZE=\"6\" FACE=\"courier\" COLOR=blue>
	<MARQUEE WIDTH=100% BEHAVIOR=ALTERNATE BGColor=yellow> 
	WELCOME TO MY WEB PAGE, 
	<%= user.getNickname() %>!!!
	</MARQUEE></FONT>
	<BLINK><a target="_top" href="<%= userService.createLogoutURL("http://" + request.getServerName() + ":" + request.getServerPort() ) %>">sign out</a></BLINK>

<%
    } else {
%>

	<FONT SIZE=\"6\" FACE=\"courier\" COLOR=blue>
	<MARQUEE WIDTH=100% BEHAVIOR=ALTERNATE BGColor=yellow> 
	WELCOME TO MY WEB PAGE!!!
	</MARQUEE></FONT>
	
	<BLINK><a target="_top" href="<%= userService.createLoginURL("http://" + request.getServerName() + ":" + request.getServerPort()) %>">SIGN IN FOR A GOOD TIME</a></BLINK>

<%
    }
%>

<%
    PersistenceManager pm = PMF.get().getPersistenceManager();
    String query = "select from " + Greeting.class.getName() + " order by date desc";
    List<Greeting> greetings = (List<Greeting>) pm.newQuery(query).execute();
    if (greetings.isEmpty()) {
%>
<p>The guestbook has no messages.</p>
<%
    } else {
%>
<table border="2">
<%  
        for (Greeting g : greetings) {
            if (g.getAuthor() == null) {
%>
<tr><td><img src="/images/ball.gif">An anonymous person wrote:</td>
<%
            } else {
%>
<tr><td><img src="/images/ball.gif"><b><%= g.getAuthor().getNickname() %></b> wrote:</td>
<%
            }
%>
<td>&nbsp;<%= g.getContent().replaceAll("<script>|</script>","") %></td></tr>
<%
        }
%>
</table>
<% 
    }
    pm.close();
%>
	<form action="/sign" method="post">
	    <div><textarea name="content" rows="3" cols="60"></textarea></div>
	    <div><input type="reset" value="RESET FORM"/><input type="submit" value="SUBMIT" /></div>
	</form>
  
  <jsp:include page="webring.html" />

<br>

  </body>
</html>