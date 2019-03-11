//
//  StockTableViewController.swift
//  DIYWealth
//
//  Created by John Walker on 25/01/2019.
//  Copyright © 2019 DIYWealth. All rights reserved.
//

import UIKit

class StockTableViewController: UITableViewController {
    
    //MARK: Properties
    
    var stocks = [Stock]()
    

    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Load the sample data.
        loadSampleStocks()

        // Uncomment the following line to preserve selection between presentations
        // self.clearsSelectionOnViewWillAppear = false

        // Uncomment the following line to display an Edit button in the navigation bar for this view controller.
        // self.navigationItem.rightBarButtonItem = self.editButtonItem
    }

    // MARK: - Table view data source

    override func numberOfSections(in tableView: UITableView) -> Int {
        return 1
    }

    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        // #warning Incomplete implementation, return the number of rows
        return stocks.count
    }

    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        
        // Table view cells are reused and should be dequeued using a cell identifier.
        let cellIdentifier = "StockTableViewCell"
        
        guard let cell = tableView.dequeueReusableCell(withIdentifier: cellIdentifier, for: indexPath) as? StockTableViewCell  else {
            fatalError("The dequeued cell is not an instance of StockTableViewCell.")
        }
        
        // Fetches the appropriate stock for the data source layout.
        let stock = stocks[indexPath.row]
        
        cell.symbolLabel.text = stock.symbol
        cell.nameLabel.text = stock.name
        cell.rankLabel.text = String(stock.rank) + "."
        cell.peLabel.text = "PE: " + String(stock.pe)
        cell.roeLabel.text = "ROE: " + String(stock.roe)
        cell.marketcapLabel.text = "MCAP: " + String(stock.marketcap)

        return cell
    }
    
    override func tableView(_ tableView: UITableView, heightForHeaderInSection section: Int) -> CGFloat {
        return 125
    }
    
    override func tableView(_ tableView: UITableView, viewForHeaderInSection section: Int) -> UIView? {
        
        let cellIdentifier = "StockHeaderCell"
        
        guard let headerCell = tableView.dequeueReusableCell(withIdentifier: cellIdentifier) as? StockHeaderCell else {
            fatalError("The dequeued cell is not an instance of StockHeaderCell.")
        }
        //headerCell.backgroundColor = UIColor.cyanColor()
        //headerCell.headerLabel.text = "Europe"
        
        return headerCell
    }

    /*
    // Override to support conditional editing of the table view.
    override func tableView(_ tableView: UITableView, canEditRowAt indexPath: IndexPath) -> Bool {
        // Return false if you do not want the specified item to be editable.
        return true
    }
    */

    /*
    // Override to support editing the table view.
    override func tableView(_ tableView: UITableView, commit editingStyle: UITableViewCellEditingStyle, forRowAt indexPath: IndexPath) {
        if editingStyle == .delete {
            // Delete the row from the data source
            tableView.deleteRows(at: [indexPath], with: .fade)
        } else if editingStyle == .insert {
            // Create a new instance of the appropriate class, insert it into the array, and add a new row to the table view
        }    
    }
    */

    /*
    // Override to support rearranging the table view.
    override func tableView(_ tableView: UITableView, moveRowAt fromIndexPath: IndexPath, to: IndexPath) {

    }
    */

    /*
    // Override to support conditional rearranging of the table view.
    override func tableView(_ tableView: UITableView, canMoveRowAt indexPath: IndexPath) -> Bool {
        // Return false if you do not want the item to be re-orderable.
        return true
    }
    */

    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destination.
        // Pass the selected object to the new view controller.
    }
    */
    
    //MARK: Private Methods
    
    private func loadSampleStocks() {
        
        guard let stock1 = Stock(symbol: "AAA", name: "Asrakjnsskd", rank: 1, pe: 1.0, roe: 33.2, marketcap: 51.0) else {
            fatalError("Unable to instantiate stock1")
        }
        guard let stock2 = Stock(symbol: "AAB", name: "Ajsjdrmnrnf", rank: 2, pe: 1.1, roe: 32.2, marketcap: 81.0) else {
            fatalError("Unable to instantiate stock2")
        }
        guard let stock3 = Stock(symbol: "AAC", name: "Assnmdnfbjh", rank: 3, pe: 1.2, roe: 31.2, marketcap: 92.0) else {
            fatalError("Unable to instantiate stock3")
        }
        guard let stock4 = Stock(symbol: "AAD", name: "Adfgrvnkaoo", rank: 4, pe: 1.3, roe: 30.2, marketcap: 1000.0) else {
            fatalError("Unable to instantiate stock4")
        }
        guard let stock5 = Stock(symbol: "AAE", name: "Asdjjdfjbeg", rank: 5, pe: 1.4, roe: 29.2, marketcap: 1500.0) else {
            fatalError("Unable to instantiate stock5")
        }
        guard let stock6 = Stock(symbol: "AAF", name: "Asjkjfhauwh", rank: 6, pe: 1.5, roe: 28.2, marketcap: 63.0) else {
            fatalError("Unable to instantiate stock6")
        }
        guard let stock7 = Stock(symbol: "AAG", name: "Asdnsjekweb", rank: 7, pe: 1.6, roe: 27.2, marketcap: 72.0) else {
            fatalError("Unable to instantiate stock7")
        }
        guard let stock8 = Stock(symbol: "AAH", name: "Akdsjfhwehj", rank: 8, pe: 1.7, roe: 26.2, marketcap: 19995.0) else {
            fatalError("Unable to instantiate stock8")
        }
        guard let stock9 = Stock(symbol: "AAI", name: "Asjkdjsfkej", rank: 9, pe: 1.8, roe: 26.2, marketcap: 82.0) else {
            fatalError("Unable to instantiate stock9")
        }
        guard let stock10 = Stock(symbol: "AAJ", name: "Akslkdnsjdf", rank: 10, pe: 1.9, roe: 24.2, marketcap: 20000.0) else {
            fatalError("Unable to instantiate stock10")
        }
        guard let stock11 = Stock(symbol: "AAK", name: "Ajsdksjdksj", rank: 11, pe: 2.0, roe: 23.2, marketcap: 62.0) else {
            fatalError("Unable to instantiate stock11")
        }
        guard let stock12 = Stock(symbol: "AAL", name: "Asnsddsdhdb", rank: 12, pe: 2.1, roe: 22.2, marketcap: 100000.0) else {
            fatalError("Unable to instantiate stock12")
        }
        guard let stock13 = Stock(symbol: "AAM", name: "Aansmnssbns", rank: 13, pe: 2.2, roe: 21.2, marketcap: 153.0) else {
            fatalError("Unable to instantiate stock13")
        }
        guard let stock14 = Stock(symbol: "AAN", name: "Aseopejrjdn", rank: 14, pe: 2.3, roe: 20.2, marketcap: 2000.0) else {
            fatalError("Unable to instantiate stock14")
        }
        guard let stock15 = Stock(symbol: "AAO", name: "Aqwjkfjkjbd", rank: 15, pe: 2.4, roe: 19.2, marketcap: 3000.0) else {
            fatalError("Unable to instantiate stock15")
        }
        guard let stock16 = Stock(symbol: "AAP", name: "Asodpofjenr", rank: 16, pe: 2.5, roe: 18.2, marketcap: 35000.0) else {
            fatalError("Unable to instantiate stock16")
        }
        guard let stock17 = Stock(symbol: "AAQ", name: "Asodifjoiej", rank: 17, pe: 2.6, roe: 17.2, marketcap: 2700.0) else {
            fatalError("Unable to instantiate stock17")
        }
        guard let stock18 = Stock(symbol: "AAR", name: "Asjdksjfnek", rank: 18, pe: 2.7, roe: 16.2, marketcap: 197.0) else {
            fatalError("Unable to instantiate stock18")
        }
        guard let stock19 = Stock(symbol: "AAS", name: "Asdksjfkjnw", rank: 19, pe: 2.8, roe: 15.2, marketcap: 93.0) else {
            fatalError("Unable to instantiate stock19")
        }
        guard let stock20 = Stock(symbol: "AAT", name: "Asdkdjfkjen", rank: 20, pe: 2.9, roe: 14.2, marketcap: 25000.0) else {
            fatalError("Unable to instantiate stock20")
        }
        guard let stock21 = Stock(symbol: "AAU", name: "Aajskcjdnie", rank: 21, pe: 3.0, roe: 13.2, marketcap: 63.0) else {
            fatalError("Unable to instantiate stock21")
        }
        guard let stock22 = Stock(symbol: "AAV", name: "Akdlkdflerj", rank: 22, pe: 3.1, roe: 12.2, marketcap: 199000.0) else {
            fatalError("Unable to instantiate stock22")
        }
        guard let stock23 = Stock(symbol: "AAW", name: "Apeoweirwhf", rank: 23, pe: 3.2, roe: 11.2, marketcap: 72.0) else {
            fatalError("Unable to instantiate stock23")
        }
        
        stocks += [stock1, stock2, stock3, stock4, stock5, stock6, stock7, stock8, stock9, stock10, stock11, stock12, stock13, stock14, stock15, stock16, stock17, stock18, stock19, stock20, stock21, stock22, stock23]
        
    }

}
