import java.io.File;

import javax.xml.transform.Source;
import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.Schema;
import javax.xml.validation.SchemaFactory;
import javax.xml.validation.Validator;

import org.xml.sax.ErrorHandler;
import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;


/**
 * Compile and run this from the parent directory.
 */
public class SchemaConformance implements ErrorHandler {

  public static void main(final String[] args) throws Exception {
    System.exit(new SchemaConformance().run());
  }

  private int _errors;

  private int run() throws Exception {
    SchemaFactory schemaFactory = SchemaFactory.newInstance(javax.xml.XMLConstants.W3C_XML_SCHEMA_NS_URI);
    Schema schema = schemaFactory.newSchema(new Source[] {
        new StreamSource(new File("../schema/inlinexbrl-3_0-transformation.xsd")),
        new StreamSource(new File("tests.xsd"))
    });
    final Validator validator = schema.newValidator();
    validator.setErrorHandler(this);
    final StreamSource source = new StreamSource(new File("valid.xml"));
    validator.validate(source);
    return _errors;
  }


  @Override
  public void warning(final SAXParseException exception) throws SAXException {
    print(exception);
  }

  @Override
  public void fatalError(final SAXParseException exception) throws SAXException {
    print(exception);
  }

  @Override
  public void error(final SAXParseException exception) throws SAXException {
    print(exception);
  }

  protected void print(final SAXParseException exception) {
    _errors++;
    System.err.println(exception);
  }
}
