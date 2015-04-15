% for o in objects :
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Untitled Document</title>
<style type="text/css">
body{
  margin:0;
  padding:0;
}
</style>
</head>

<body>
  <table cellspacing="0" cellpadding="0" style="width:100%;">
    <thead>
            <tr style="height:240px;vertical-align:bottom;">
                <th colspan="5"> 
                    <table width="100%" border="0">
                      <tr>
                        <td style="vertical-align:top;">
                          <p>${o.partner_id.name}<br />
                          </p>
                        </td>
                        <td style="vertical-align:bottom;margin-top:50px;" width="300">
                          ${o.name}
                        <br/><br />${o.date_invoice}</td>
                      </tr>
                    </table>
                </th>
            </tr>
            <tr>
              <th width="10px">&nbsp;</th>
              <th width="100px">&nbsp;</th>
              <th width="300px">&nbsp;</th>
              <th width="180px">&nbsp;</th>
              <th>&nbsp;</th>
          </tr>
        </thead>
        <tfoot>
            <tr>
                <td colspan="4">&nbsp;</td>
                <td>&nbsp;</td>
              </tr>
              <tr>
                <td colspan="4">&nbsp;</td>
                <td>&nbsp;</td>
              </tr>
              <tr>
                <td colspan="4">&nbsp;</td>
                <td>&nbsp;</td>
              </tr>
              <tr>
                <td colspan="4">&nbsp;</td>
                <td>${o.amount_untaxed}</td>
              </tr>
              <tr>
                <td colspan="4">&nbsp;</td>
                <td>${o.amount_tax}</td>
              </tr>
              <tr>
                <td colspan="4">&nbsp;</td>
                <td>${o.amount_total}</td>
              </tr>
              <tr>
                <td colspan="5" style="height:5cm;">&nbsp;</td>
              </tr>
            
        </tfoot>
        
        
        <tbody>
            
              
              <tr valign="top" style="height:10cm;">
                <td colspan="5">
                  <table width="100%" cellpadding="9" cellspacing="0" style="border-collapse:collapse;border:1px;margin-top:10px;">
                  % for k,l in enumerate(o.invoice_line) :
                      <tr>
                      
                          <td style="text-align:left;" width="6%">${ k+1 }</td>
                          <td style="text-align:left;" width="14%">                       
                              ${ l.quantity }
                            </td>
                            <td style="text-align:left;" width="50%">
                              ${ l.name }
                            </td>
                            <td style="text-align:left;" width="15%">
                              ${ l.price_unit }
                            </td>
                            <td style="text-align:left;" width="15%">
                              ${ l.price_subtotal }
                            </td>
                        </tr>
                    % endfor
                    </table>
                </td>
              </tr>
        </tbody>
        
    </table>
</body>
</html>
% endfor
