/*
 * (C) Koninklijke Philips Electronics N.V. 2018
 *
 * All rights are reserved. Reproduction or transmission in whole or in part, in any form or by any
 * means, electronic, mechanical or otherwise, is prohibited without the prior written consent of
 * the copyright owner.
 *
 */

package suite;

import static junit.framework.TestCase.assertTrue;
import java.io.File;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.logging.Logger;
import org.apache.commons.io.FileUtils;
import org.junit.BeforeClass;
import org.junit.Test;
import com.intuit.karate.StringUtils;
import com.intuit.karate.cucumber.CucumberRunner;
import com.intuit.karate.cucumber.KarateStats;
import cucumber.api.CucumberOptions;
import net.masterthought.cucumber.Configuration;
import net.masterthought.cucumber.ReportBuilder;

@CucumberOptions (tags = { "~@ignore" }) // important: do not use @RunWith(Karate.class) !
public class ApiTestParallelTest {

  private static final String CICD = "cicd";
  private static final Logger LOG = Logger.getLogger ("ParallelTest");

  @BeforeClass
  public static void setup () throws Exception {

    if (!CICD.equalsIgnoreCase (System.getProperty ("karate.env"))) {
      return;
    }
  }

  @Test
  public void testParallel () {

    String karateOutputPath = "target/surefire-reports";
    String tc = System.getProperty ("karate.tc");
    int threadCount = 20; // Default thread count
    if (!StringUtils.isBlank (tc)) {
      threadCount = Integer.parseInt (tc);
    }

    LOG.info ("STARTING: Parallel Test Execution...");
    KarateStats stats = CucumberRunner.parallel (getClass (), threadCount, karateOutputPath);
    generateReport (karateOutputPath);
    LOG.info ("COMPLETED: Parallel Test Execution.");
    assertTrue ("There are suite scenario failures", stats.getFailCount () == 0);
  }

  private static void generateReport (String karateOutputPath) {

    Collection<File> jsonFiles =
        FileUtils.listFiles (new File (karateOutputPath), new String[] { "json" }, true);
    List<String> jsonPaths = new ArrayList<> (jsonFiles.size ());
    jsonFiles.forEach (file -> jsonPaths.add (file.getAbsolutePath ()));
    Configuration config = new Configuration (new File ("target"), "HealthSuite Platform Service TestSuite");
    ReportBuilder reportBuilder = new ReportBuilder (jsonPaths, config);
    reportBuilder.generateReports ();
  }
}
