function init () {
  var env = karate.env; // get system property 'karate.env'
  karate.log ('karate.env system property was:', env);
  if (!env) {
    env = 'cicd';
  }

  var configFile = 'classpath:' + env + '.json';
  try {
      config = karate.read (configFile);
      karate.configure ('connectTimeout', 900000);
      karate.configure ('readTimeout', 900000);
      if (config.enable_proxy) {
          karate.configure ('proxy', config.proxy);
      }

  } catch (e) {
      karate.log ("Failed to initialize test setup configuration - ", e);
  }
  return config;
}