//
//  StockTableViewCell.swift
//  DIYWealth
//
//  Created by John Walker on 25/01/2019.
//  Copyright © 2019 DIYWealth. All rights reserved.
//

import UIKit

class StockTableViewCell: UITableViewCell {
    
    //MARK: Properties
    //@IBOutlet weak var symbolLabel: UILabel!
    //@IBOutlet weak var nameLabel: UILabel!
    //@IBOutlet weak var rankLabel: UILabel!
    //@IBOutlet weak var peLabel: UILabel!
    //@IBOutlet weak var roeLabel: UILabel!
    @IBOutlet weak var rankLabel: UILabel!
    @IBOutlet weak var symbolLabel: UILabel!
    @IBOutlet weak var nameLabel: UILabel!
    @IBOutlet weak var peLabel: UILabel!
    @IBOutlet weak var roeLabel: UILabel!
    @IBOutlet weak var marketcapLabel: UILabel!
    
    override func awakeFromNib() {
        super.awakeFromNib()
        // Initialization code
    }

    override func setSelected(_ selected: Bool, animated: Bool) {
        super.setSelected(selected, animated: animated)

        // Configure the view for the selected state
    }

}
