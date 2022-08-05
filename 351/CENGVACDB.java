package ceng.ceng351.cengvacdb;

import javax.swing.plaf.nimbus.State;
import java.sql.*;

public class CENGVACDB implements ICENGVACDB{

    /********* variables **********/
    private static Connection connection = null;

    private static String user = "e2381028"; // Your userName
    private static String password = "d9Kv?2UJXz%P"; //  Your password
    private static String host = "144.122.71.121"; // host name
    private static String database = "db2381028"; // Your database name
    private static int port = 8080; // port

    /********* assignment methods ***********/

    @Override
    public void initialize() {
        createConnection();
    }

    @Override
    public int createTables() {
        String[] commands = createTableCommands();

        return  createTable(commands[0])
                + createTable(commands[1])
                + createTable(commands[2])
                + createTable(commands[3])
                + createTable(commands[4]);
    }

    @Override
    public int dropTables() {
        String[] commands = dropTableCommands();

        /* due to key constraints, we need to make a new order of commands */
        return dropTable(commands[4])
                + dropTable(commands[2])
                + dropTable(commands[0])
                + dropTable(commands[3])
                + dropTable(commands[1]);
    }

    @Override
    public ceng.ceng351.cengvacdb.Vaccine[] getVaccinesNotAppliedAnyUser() {
        /*
        Output: code, vaccinename, type
        Order the results by code in ascending order
         */

        ceng.ceng351.cengvacdb.Vaccine[] notApplied = null;
        int size = 0;

        /* query */
        String s = "SELECT DISTINCT V.code, V.vaccinename, V.type " +
                   "FROM Vaccine V " +
                   "WHERE V.code NOT IN (SELECT N.code FROM Vaccination N) " +
                   "ORDER BY V.code ASC";

        /* initialize the array and find its size */
        try {
            Statement statement = connection.createStatement();

            ResultSet result = statement.executeQuery(s); // result of the query

            while(result.next()) size++; // find size of array (row count)

            notApplied = new Vaccine[size]; // create array
        }
        catch (SQLException e) {
            e.printStackTrace();
        }

        /* insert Vaccines from result set into array */
        try{
            Statement statement = connection.createStatement();

            ResultSet result = statement.executeQuery(s);

            int i = 0; // index for array
            while(result.next()){
                /* variables of vaccine */
                int code = result.getInt("code");
                String name = result.getString("vaccinename");
                String type = result.getString("type");

                /* new vaccine */
                Vaccine v = new Vaccine(code,name,type);

                /* insert into array */
                if(notApplied != null) {
                    notApplied[i++] = v;
                }
            }
        }
        catch (SQLException e){
            e.printStackTrace();
        }

        return notApplied;
    }

    @Override
    public ceng.ceng351.cengvacdb.QueryResult.UserIDuserNameAddressResult[] getVaccinatedUsersforTwoDosesByDate(String vacdate) {
        /*
        Input: vacdate
        Output: userID, userName, address
        Order the results by userID in ascending order
         */

        QueryResult.UserIDuserNameAddressResult[] users = null;
        int size = 0;

        /* query */
        String s = "SELECT U.userID, U.userName, U.address " +
                "FROM User U, Vaccination V " +
                "WHERE U.userID = V.userID AND " +
                "V.dose = 1 AND " +
                "V.vacdate >= " + "'" + vacdate + "'" +
                " AND U.userID IN " +
                "(SELECT U2.userID FROM User U2, Vaccination V2 WHERE U2.userID = V2.userID AND V2.dose = 2 AND" +
                " V2.vacdate >= " + "'" + vacdate + "'" +
                ")" +
                "AND U.userID NOT IN " +
                "(SELECT U3.userID FROM User U3, Vaccination V3 WHERE U3.userID = V3.userID AND V3.dose > 2)" +
                " ORDER BY userID ASC";

        // firstly search for dose 1, then search for dose 2, finally search whether the user has been vaccinated more than 2


        /* initialize the array and find its size */
        try{
            Statement statement = connection.createStatement();

            ResultSet result = statement.executeQuery(s);

            while(result.next()) size++; // find the number of users (row count)

            users = new QueryResult.UserIDuserNameAddressResult[size];

        }

        catch (SQLException e){
            e.printStackTrace();
        }


        /* insert Users from result set into array */
        try{
            Statement statement = connection.createStatement();

            ResultSet result = statement.executeQuery(s);

            int i = 0; // index for array
            while(result.next()){
                /* variables of user */
                String userID = Integer.toString(result.getInt("userID"));
                String userName = result.getString("userName");
                String address = result.getString("address");

                /* new user */
                QueryResult.UserIDuserNameAddressResult u = new QueryResult.UserIDuserNameAddressResult(userID,userName,address);

                /* insert into array */
                if(users != null) {
                    users[i++] = u;
                }
            }
        }

        catch (SQLException e){
            e.printStackTrace();
        }

        return users;
    }

    @Override
    public ceng.ceng351.cengvacdb.Vaccine[] getTwoRecentVaccinesDoNotContainVac() {
        /*
        Output: code, vaccinename, type
        Order the results by code in ascending order
        */
        ceng.ceng351.cengvacdb.Vaccine[] vaccines = null;


        String s = "SELECT DISTINCT V.code, V.vaccinename, V.type, MAX(T.vacdate) " +
                "FROM Vaccine V, Vaccination T " +
                "WHERE V.code = T.code AND " +
                "V.vaccinename NOT LIKE " + "'%vac%'"  +
                "GROUP BY V.code, V.vaccinename, V.type " +
                "HAVING MAX(T.vacdate) " +
                "ORDER BY MAX(T.vacdate) ASC";


        try {
            Statement statement = connection.createStatement();

            ResultSet result = statement.executeQuery(s);

            vaccines = new Vaccine[2];
            Vaccine v1 = null,v2 = null;

            if(result.last()) {
                int code1 = result.getInt("code");
                String name1 = result.getString("vaccinename");
                String type1 = result.getString("type");

                /* new vaccine */
                v1 = new Vaccine(code1, name1, type1);
            }

            if(result.previous()) {
                int code2 = result.getInt("code");
                String name2 = result.getString("vaccinename");
                String type2 = result.getString("type");

                /* new vaccine */
                v2 = new Vaccine(code2, name2, type2);
            }

            if(v1.getCode() > v2.getCode()){
                vaccines[0] = v2;
                vaccines[1] = v1;
            }
            else{
                vaccines[0] = v1;
                vaccines[1] = v2;
            }

        }
        catch (SQLException e) {
            e.printStackTrace();
        }

        return vaccines;
    }

    @Override
    public ceng.ceng351.cengvacdb.QueryResult.UserIDuserNameAddressResult[] getUsersAtHasLeastTwoDoseAtMostOneSideEffect() {
        /*
        Output: userID, userName, address
        Order the results by userID in ascending order
        */
        QueryResult.UserIDuserNameAddressResult[] users = null;
        int size = 0;

        String s = "SELECT DISTINCT U.userID, U.userName, U.address " +
                "FROM User U " +
                "WHERE U.userID IN (SELECT DISTINCT U2.userID " +
                "FROM User U2, Vaccination V2, Seen S2, AllergicSideEffect A2 " +
                "WHERE U2.userID = V2.userID AND V2.dose >= 2 AND " +
                "U2.userID = S2.userID AND " +
                "S2.effectcode = A2.effectcode AND V2.code = S2.code " +
                "GROUP BY U2.userID " +
                "HAVING COUNT(*) <= 1) " +
                "OR " +
                "U.userID IN (SELECT DISTINCT U3.userID " +
                "FROM User U3, Vaccination V3 " +
                "WHERE U3.userID = V3.userID AND U3.userID NOT IN (SELECT S3.userID FROM Seen S3) AND V3.dose >= 2) " +
                "ORDER BY U.userID ASC";

        try {
            Statement statement = connection.createStatement();

            ResultSet result = statement.executeQuery(s);

            while(result.next()) size++;
            users = new QueryResult.UserIDuserNameAddressResult[size];

        }
        catch (SQLException e) {
            e.printStackTrace();
        }

        /* insert Users from result set into array */
        try{
            Statement statement = connection.createStatement();

            ResultSet result = statement.executeQuery(s);

            int i = 0; // index for array
            while(result.next()){
                /* variables of user */
                String userID = Integer.toString(result.getInt("userID"));
                String userName = result.getString("userName");
                String address = result.getString("address");

                /* new user */
                QueryResult.UserIDuserNameAddressResult u = new QueryResult.UserIDuserNameAddressResult(userID,userName,address);

                /* insert into array */
                if(users != null) {
                    users[i++] = u;
                }
            }
        }

        catch (SQLException e){
            e.printStackTrace();
        }

        return users;
    }


    @Override
    public ceng.ceng351.cengvacdb.QueryResult.UserIDuserNameAddressResult[] getVaccinatedUsersWithAllVaccinesCanCauseGivenSideEffect(String effectname) {
        /*
        Input: effectname
        Output: userID, userName, address
        Order the results by userID in ascending order
        */

        QueryResult.UserIDuserNameAddressResult[] users = null;
        int size = 0;

        /* Vaccines that cause the given side effect */
        String s1 = "SELECT V.code " +
                "FROM Vaccine V, Seen S, AllergicSideEffect A " +
                "WHERE V.code = S.code AND S.effectcode = A.effectcode AND A.effectname = " + "'" + effectname + "'";

        String s = "SELECT DISTINCT U.userID, U.userName, U.address " +
                "FROM User U, Vaccination T " +
                "WHERE U.userID = T.userID AND T.code IN (" + s1 + ") " +
                "ORDER BY U.userID ASC";


        /* initialize the array and find its size */
        try{
            Statement statement = connection.createStatement();

            ResultSet result = statement.executeQuery(s);
            while(result.next()) size++; // find the number of users (row count)

            users = new QueryResult.UserIDuserNameAddressResult[size];
        }

        catch (SQLException e){
            e.printStackTrace();
        }


        /* insert Users from result set into array */
        try{
            Statement statement = connection.createStatement();

            ResultSet result = statement.executeQuery(s);


            int i = 0;
            while(result.next()){
                /* variables of user */
                String userID = Integer.toString(result.getInt("userID"));
                String userName = result.getString("userName");
                String address = result.getString("address");

                /* new user */
                QueryResult.UserIDuserNameAddressResult u = new QueryResult.UserIDuserNameAddressResult(userID,userName,address);

                /* insert into array */
                if(users != null) {
                    users[i++] = u;
                }

            }

        }

        catch (SQLException e){
            e.printStackTrace();
        }

        return users;
    }

    @Override
    public ceng.ceng351.cengvacdb.QueryResult.UserIDuserNameAddressResult[] getUsersWithAtLeastTwoDifferentVaccineTypeByGivenInterval(String startdate, String enddate) {
        /*
        You should include dateStart and dateEnd in the result, it is a CLOSED interval. Input: startDate, endDate
        Output: userID, userName, address
        Order the results by userID in ascending order
        */

        QueryResult.UserIDuserNameAddressResult[] users = null;
        int size = 0;


        String s = "SELECT DISTINCT U.userID, U.userName, U.address " +
                "FROM User U, Vaccination T1, Vaccination T2 " +
                "WHERE U.userID = T1.userID AND U.userID = T2.userID " +
                "AND T1.code <> T2.code " +
                "AND (T2.vacdate - T1.vacdate) <= " + "'" + enddate + "'" + " - " + "'" + startdate + "'" +
                " ORDER BY U.userID ASC";


        /* initialize the array and find its size */
        try{
            Statement statement = connection.createStatement();

            ResultSet result = statement.executeQuery(s);
            while(result.next()) size++; // find the number of users (row count)

            users = new QueryResult.UserIDuserNameAddressResult[size];

        }

        catch (SQLException e){
            e.printStackTrace();
        }


        /* insert Users from result set into array */
        try{
            Statement statement = connection.createStatement();

            ResultSet result = statement.executeQuery(s);


            int i = 0;
            while(result.next()){
                /* variables of user */
                String userID = Integer.toString(result.getInt("userID"));
                String userName = result.getString("userName");
                String address = result.getString("address");

                /* new user */
                QueryResult.UserIDuserNameAddressResult u = new QueryResult.UserIDuserNameAddressResult(userID,userName,address);

                /* insert into array */
                if(users != null) {
                    users[i++] = u;
                }
            }

        }

        catch (SQLException e){
            e.printStackTrace();
        }

        return users;
    }

    @Override
    public ceng.ceng351.cengvacdb.AllergicSideEffect[] getSideEffectsOfUserWhoHaveTwoDosesInLessThanTwentyDays() {
        // TODO
        /*Output: effectcode, effectname
        Order the results by effectcode in ascending order
        */
        int size = 0;
        AllergicSideEffect effects[] = null;

        String s = "SELECT A.effectcode, A.effectname " +
                "FROM AllergicSideEffect A, Seen S, Vaccination T " +
                "WHERE A.effectcode = S.effectcode AND S.code = T.code AND T.userID = S.userID AND T.dose = 1 " +
                "AND T.code IN (SELECT T1.code FROM Vaccination T1 WHERE T1.userID = T.userID AND DATEDIFF(T1.vacdate, T.vacdate)< 20 AND T1.dose = 2 ) " +
                "ORDER BY A.effectcode ASC";

        try {
            Statement statement = connection.createStatement();

            ResultSet result = statement.executeQuery(s);

            while(result.next()) size++;

            effects = new AllergicSideEffect[size];

        }
        catch (SQLException e) {
            e.printStackTrace();
        }
        try {
            Statement statement = connection.createStatement();

            ResultSet result = statement.executeQuery(s);

            int index = 0;
            while(result.next()){
                int code = result.getInt("effectcode");
                String name = result.getString("effectname");

                AllergicSideEffect e = new AllergicSideEffect(code,name);

                if(effects != null)
                    effects[index++] = e;
            }

        }
        catch (SQLException e) {
            e.printStackTrace();
        }
        return effects;
    }

    @Override
    public double averageNumberofDosesofVaccinatedUserOverSixtyFiveYearsOld() {
        double avg = 0.0;
        int size = 0;

        String s = "SELECT COUNT(V.code) AS 'COUNT' , U.userID " +
                "FROM User U, Vaccination V " +
                "WHERE U.userID = V.userID AND U.age > 65 " +
                "GROUP BY U.userID";

        try{
            Statement statement = connection.createStatement();

            ResultSet result = statement.executeQuery(s);

            while (result.next()){
                avg += result.getInt("COUNT");
                size ++;
            }

        }
        catch (SQLException e){
            e.printStackTrace();
        }

        return avg/size;
    }

    @Override
    public int updateStatusToEligible(String givendate) {
        int result = 0;


        String s = "UPDATE User " +
                "SET status = 'Eligible' " +
                "WHERE userID IN (SELECT T.userID FROM Vaccination T WHERE userID = T.userID AND status = 'Not_Eligible' GROUP BY T.userID HAVING DATEDIFF(" + "'" + givendate + "'" + ", MAX(T.vacdate)) >= 120)";

        try{

            Statement statement = connection.createStatement();

            result = statement.executeUpdate(s);


        }
        catch (SQLException e){
            e.printStackTrace();
        }
        return result;
    }

    @Override
    public ceng.ceng351.cengvacdb.Vaccine deleteVaccine(String vaccineName) {
        // TODO
        ceng.ceng351.cengvacdb.Vaccine vaccine = null;
        String s = "DELETE FROM Vaccine V WHERE V.vaccinename = " + "'" + vaccineName + "'";
        String select = "SELECT V.code, V.vaccinename, V.type FROM Vaccine V WHERE V.vaccinename = " + "'" + vaccineName + "'";


        try {
            Statement statement = connection.createStatement();

            ResultSet result = statement.executeQuery(select);

            result.next();
            int code = result.getInt("code");
            String name = result.getString("vaccinename");
            String type = result.getString("type");

            vaccine = new Vaccine(code,name,type);
        }
        catch (SQLException e) {
            e.printStackTrace();
        }
        try {
            Statement statement = connection.createStatement();

            statement.execute(s);

        }
        catch (SQLException e) {
            e.printStackTrace();
        }

        return vaccine;
    }

    @Override
    public int insertSeen(ceng.ceng351.cengvacdb.Seen[] seens) {
        int out = 0; // number of seen statements that correctly inserted

        try {
            Statement statement = connection.createStatement();

            for(Seen seen : seens){
                String s = "INSERT INTO Seen (effectcode, code, userID, date, degree) " +
                        "VALUES (" +
                        Integer.toString(seen.getEffectcode()) +
                        "," +

                         Integer.toString(seen.getCode()) +
                        "," +

                        "'" + seen.getUserID() + "'" +
                        "," +

                        "'" + seen.getDate() + "'" +
                        "," +

                        "'" + seen.getDegree() + "'" +
                        ")";


                statement.executeUpdate(s); // insert into the table


                out++;
            }
        }

        catch (SQLException e) {
            e.printStackTrace();
        }
        return out;
    }

    @Override
    public int insertVaccination(ceng.ceng351.cengvacdb.Vaccination[] vaccinations) {
        int out = 0; // number of vaccinations that correctly inserted

        try {
            Statement statement = connection.createStatement();

            for(Vaccination vaccination : vaccinations){
                String s = "INSERT INTO Vaccination (code, userID, dose, vacdate)" +
                        "VALUES (" +
                        Integer.toString(vaccination.getCode()) +
                        "," +

                        Integer.toString(vaccination.getUserID()) +
                        "," +

                        Integer.toString(vaccination.getDose()) +
                        "," +

                        "'" + vaccination.getVacdate() + "'" +
                        ")";


                statement.executeUpdate(s); // insert into the table


                out++;
            }
        }

        catch (SQLException e) {
            e.printStackTrace();
        }
        return out;
    }

    @Override
    public int insertVaccine(ceng.ceng351.cengvacdb.Vaccine[] vaccines) {
        int out = 0; // number of vaccines that correctly inserted

        try {
            Statement statement = connection.createStatement();

            for(Vaccine vaccine : vaccines){
                String s = "INSERT INTO Vaccine (code, vaccinename, type) " +
                        "VALUES (" +
                        Integer.toString(vaccine.getCode()) +
                        "," +
                        "'" + vaccine.getVaccineName() + "'" +
                        "," +
                        "'" + vaccine.getType() + "'" +
                        ")";


                statement.executeUpdate(s); // insert into the table


                out++;
            }
        }

        catch (SQLException e) {
            e.printStackTrace();
        }
        return out;
    }

    @Override
    public int insertAllergicSideEffect(ceng.ceng351.cengvacdb.AllergicSideEffect[] sideEffects) {
        int out = 0; // number of side effects that correctly inserted

        try {
            Statement statement = connection.createStatement();

            for(AllergicSideEffect effect : sideEffects){
                String s = "INSERT INTO AllergicSideEffect (effectcode, effectname) " +
                        "VALUES (" +
                        Integer.toString(effect.getEffectCode()) +
                        "," +
                        "'" + effect.getEffectName() + "'" +
                        ")";


                statement.executeUpdate(s); // insert into the table


                out++;
            }
        }

        catch (SQLException e) {
            e.printStackTrace();
        }
        return out;
    }

    @Override
    public int insertUser(ceng.ceng351.cengvacdb.User[] users) {
        int out = 0; // number of users that correctly inserted

        try {
            Statement statement = connection.createStatement();

            for(User user : users){
                String s = "INSERT INTO User (userID, userName, age, address, password, status) " +
                        "VALUES (" +
                        Integer.toString(user.getUserID())+
                        "," +

                        "'" + user.getUserName() + "'" +
                        "," +

                        Integer.toString(user.getAge()) +
                        "," +

                        "'" + user.getAddress() + "'" +
                        "," +

                        "'" + user.getPassword() + "'" +
                        "," +

                        "'" + user.getStatus() + "'" +
                        ")";

                /* String values are needed to be given like that --> ('String Value')
                   Integer values are needed to be given in string form
                */

                statement.executeUpdate(s); // insert into the table


                out++; // if successful
            }
        }
        catch (SQLException e) {
            e.printStackTrace();
        }
        return out;
    }

    /*********** helper methods ************/

    /* initiates a connection to mySQL */
    private static void createConnection() {

        String url = "jdbc:mysql://" + host + ":" + port + "/" + database+ "?useSSL=false";

        try {
            Class.forName("com.mysql.cj.jdbc.Driver");
            connection =  DriverManager.getConnection(url, user, password);
        }
        catch (SQLException | ClassNotFoundException e) {
            e.printStackTrace();
        }
    }

    /* create sql commands to create every table */
    private String[] createTableCommands(){
        String[] commands = new String[5];


        /* user table */
        // User (userID:int, userName:varchar(30), age:int, address:varchar(150), password:varchar(30), status:varchar(15))
        commands[0] = "CREATE TABLE IF NOT EXISTS User (" +
                "userID INT," +
                "userName VARCHAR(30), " +
                "age INT, " +
                "address VARCHAR(150), " +
                "password VARCHAR(30), " +
                "status VARCHAR(15), " +
                "PRIMARY KEY (userID) )";

        /* vaccine table */
        // Vaccine (code:int, vaccinename:varchar(30), type:varchar(30))
        commands[1] = "CREATE TABLE IF NOT EXISTS Vaccine (" +
                "code INT, " +
                "vaccinename VARCHAR(30), " +
                "type VARCHAR(30), " +
                "PRIMARY KEY(code) )";

        /* vaccination table */
        // Vaccination (code:int, userID:int, dose:int, vacdate:date) References Vaccine (code), User (userID)
        commands[2] = "CREATE TABLE IF NOT EXISTS Vaccination (" +
                "code INT, " +
                "userID INT, " +
                "dose INT, " +
                "vacdate DATE, " +
                "PRIMARY KEY (code, userID,dose), " +
                "FOREIGN KEY (code) REFERENCES Vaccine (code) ON DELETE CASCADE, " +
                "FOREIGN KEY (userID) REFERENCES User (userID) )";

        /* allergicSideEffect table */
        // AllergicSideEffect (effectcode:int, effectname:varchar(50))
        commands[3] = "CREATE TABLE IF NOT EXISTS AllergicSideEffect (" +
                "effectcode INT, " +
                "effectname VARCHAR(50), " +
                "PRIMARY KEY(effectcode) )";

        /* seen table */
        // Seen (effectcode:int, code:int, userID:int, date:date, degree:varchar(30))
        // References Allergic- SideEffect (effectcode), Vaccination (code), User (userID)
        commands[4] = "CREATE TABLE IF NOT EXISTS Seen (" +
                "effectcode INT, " +
                "code INT, " +
                "userID INT, " +
                "date DATE, " +
                "degree VARCHAR(30), " +
                "PRIMARY KEY (effectcode,code,userID), " +
                "FOREIGN KEY (effectcode) REFERENCES AllergicSideEffect (effectcode), " +
                "FOREIGN KEY (code) REFERENCES Vaccination (code) ON DELETE CASCADE, " +
                "FOREIGN KEY (userID) REFERENCES User (userID) )";

        return commands;
    }

    /* create sql commands to drop every table */
    private String[] dropTableCommands(){
        String[] commands = new String[5];

        /* user table */
        commands[0] = "DROP TABLE IF EXISTS User";

        /* vaccine table */
        commands[1] = "DROP TABLE IF EXISTS Vaccine";

        /* vaccination table */
        commands[2] = "DROP TABLE IF EXISTS Vaccination";

        /* allergicSideEffect table */
        commands[3] = "DROP TABLE IF EXISTS AllergicSideEffect";

        /* seen table */
        commands[4] = "DROP TABLE IF EXISTS Seen";


        return commands;
    }

    /* creates table with given string command : SQL STATEMENT */
    private int createTable(String command){
        int created = 0;

        try {
            Statement statement = connection.createStatement();

            statement.executeUpdate(command); // say create table to mysql

            created = 1; // if successful

        }
        catch (SQLException e) {
            e.printStackTrace();
        }

        return created;
    }

    /* drops table with given string command : SQL STATEMENT */
    private int dropTable(String command){
        int dropped = 0;

        try {
            Statement statement = connection.createStatement();

            statement.executeUpdate(command); // say drop table to mysql

            dropped = 1; // if successful

        }
        catch (SQLException e) {
            e.printStackTrace();
        }

        return dropped;
    }
}
