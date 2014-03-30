
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.List;

/**
 * Test to see if we can use one socket for multiple server/clients
 *
 * @author shen
 */
public class ProofByConceptServerClient
{

    public static void main(String[] args)
    {
        List<Thread> threads = new ArrayList<>();

        for (int i = 0; i < 5; i++)
        {
            String name = "ServerClient" + i;
            Runnable sc = new ServerClient(name);
            Thread t = new Thread(sc);
            t.setName(name);
            t.start();
            threads.add(t);
        }
    }
}

class ServerClient implements Runnable
{

    private String name;

    public ServerClient(String name)
    {
        this.name = name;
    }

    @Override
    public void run()
    {
        listen();
    }

    private void listen()
    {
        int count = 0;
        int portNumber = 4200;
        InetAddress host = null;
        try
        {
            host = InetAddress.getByName("localhost");
        }
        catch (UnknownHostException ex)
        {
            System.out.println(name + " Could not resolve localhost");
        }

        assert host != null;
        try (
                ServerSocket serverSocket = new ServerSocket(portNumber);
                Socket clientSocket = serverSocket.accept();
                PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true);
                BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));)
        {
            String messageReceived;
            String messageToSend;

            if (count > 7)
            {
                messageToSend = "Bye.";
            }
            else
            {
                messageToSend = "hi I'm " + name;
            }

            while ((messageReceived = in.readLine()) != null)
            {
                System.out.println(name + ": Server has sent me: " + messageReceived);
                if (messageReceived.equals("Bye."))
                {
                    break;
                }

                assert messageToSend != null;

                System.out.println(name + ":Client is sending: " + messageToSend);
                out.println(messageToSend);
                count++;
            }
        }
        catch (IOException ioex)
        {
            System.out.println("ERROR in " + name + ": " + ioex.getMessage());
        }
    }
}
